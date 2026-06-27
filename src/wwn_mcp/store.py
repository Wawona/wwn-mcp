"""Hybrid sqlite store: FTS5 (lexical) + vectors (semantic), fused with RRF.

Vector search uses the ``sqlite-vec`` extension when present; otherwise it
falls back to brute-force cosine in Python. Indexing is incremental: chunks are
keyed by a stable id and skipped when their content hash is unchanged.
"""

from __future__ import annotations

import array
import json
import math
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from .chunk import Chunk
from .config import Settings

_FTS_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


@dataclass
class SearchResult:
    score: float
    project: str
    source: str
    kind: str
    lang: str | None
    path: str
    title: str
    text: str
    start_line: int
    end_line: int
    url: str | None
    license: str | None
    tags: dict

    def as_dict(self) -> dict:
        d = self.__dict__.copy()
        return d

    def citation(self) -> str:
        loc = f"{self.path}:{self.start_line}-{self.end_line}"
        return f"{self.project}/{self.kind} {loc}" + (f" ({self.url})" if self.url else "")


class Store:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.dim = settings.embed_dim
        self.db = sqlite3.connect(str(settings.db_path))
        self.db.row_factory = sqlite3.Row
        self._vec = self._load_vec_ext()
        self._ensure_schema()

    # --- setup --------------------------------------------------------------

    def _load_vec_ext(self) -> bool:
        try:
            import sqlite_vec  # type: ignore

            self.db.enable_load_extension(True)
            sqlite_vec.load(self.db)
            self.db.enable_load_extension(False)
            return True
        except Exception:  # noqa: BLE001 - brute-force fallback
            return False

    def _ensure_schema(self) -> None:
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS chunks (
              rowid INTEGER PRIMARY KEY AUTOINCREMENT,
              chunk_id TEXT UNIQUE NOT NULL,
              project TEXT, source TEXT, path TEXT, kind TEXT, lang TEXT,
              title TEXT, text TEXT,
              start_line INTEGER, end_line INTEGER,
              url TEXT, license TEXT, tags TEXT, content_hash TEXT,
              embedding BLOB
            );
            CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source);
            CREATE INDEX IF NOT EXISTS idx_chunks_kind ON chunks(kind);
            CREATE INDEX IF NOT EXISTS idx_chunks_project ON chunks(project);
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts
              USING fts5(chunk_id UNINDEXED, title, text);
            CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
            """
        )
        if self._vec:
            try:
                self.db.execute(
                    f"CREATE VIRTUAL TABLE IF NOT EXISTS vec_chunks "
                    f"USING vec0(rowid INTEGER PRIMARY KEY, embedding float[{self.dim}])"
                )
            except sqlite3.OperationalError:
                self._vec = False
        self.db.commit()

    # --- indexing -----------------------------------------------------------

    def existing_hashes(self, source: str) -> dict[str, str]:
        cur = self.db.execute(
            "SELECT chunk_id, content_hash FROM chunks WHERE source=?", (source,)
        )
        return {r["chunk_id"]: r["content_hash"] for r in cur.fetchall()}

    def upsert(self, chunk: Chunk, embedding: list[float]) -> None:
        blob = array.array("f", embedding).tobytes()
        cur = self.db.execute(
            """
            INSERT INTO chunks (chunk_id, project, source, path, kind, lang, title,
                                text, start_line, end_line, url, license, tags,
                                content_hash, embedding)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(chunk_id) DO UPDATE SET
              project=excluded.project, source=excluded.source, path=excluded.path,
              kind=excluded.kind, lang=excluded.lang, title=excluded.title,
              text=excluded.text, start_line=excluded.start_line,
              end_line=excluded.end_line, url=excluded.url, license=excluded.license,
              tags=excluded.tags, content_hash=excluded.content_hash,
              embedding=excluded.embedding
            """,
            (
                chunk.chunk_id, chunk.project, chunk.source, chunk.path, chunk.kind,
                chunk.lang, chunk.title, chunk.text, chunk.start_line, chunk.end_line,
                chunk.url, chunk.license, json.dumps(chunk.tags), chunk.content_hash, blob,
            ),
        )
        rowid = cur.lastrowid or self._rowid_for(chunk.chunk_id)
        self.db.execute("DELETE FROM chunks_fts WHERE chunk_id=?", (chunk.chunk_id,))
        self.db.execute(
            "INSERT INTO chunks_fts (chunk_id, title, text) VALUES (?,?,?)",
            (chunk.chunk_id, chunk.title, chunk.text),
        )
        if self._vec and rowid is not None:
            try:
                self.db.execute("DELETE FROM vec_chunks WHERE rowid=?", (rowid,))
                self.db.execute(
                    "INSERT INTO vec_chunks (rowid, embedding) VALUES (?, ?)", (rowid, blob)
                )
            except sqlite3.OperationalError:
                self._vec = False

    def _rowid_for(self, chunk_id: str) -> int | None:
        r = self.db.execute("SELECT rowid FROM chunks WHERE chunk_id=?", (chunk_id,)).fetchone()
        return r["rowid"] if r else None

    def prune(self, source: str, keep_ids: set[str]) -> int:
        cur = self.db.execute("SELECT chunk_id, rowid FROM chunks WHERE source=?", (source,))
        stale = [(r["chunk_id"], r["rowid"]) for r in cur.fetchall() if r["chunk_id"] not in keep_ids]
        for chunk_id, rowid in stale:
            self.db.execute("DELETE FROM chunks WHERE chunk_id=?", (chunk_id,))
            self.db.execute("DELETE FROM chunks_fts WHERE chunk_id=?", (chunk_id,))
            if self._vec:
                self.db.execute("DELETE FROM vec_chunks WHERE rowid=?", (rowid,))
        return len(stale)

    def reset(self) -> None:
        self.db.executescript(
            "DELETE FROM chunks; DELETE FROM chunks_fts;"
            + ("DELETE FROM vec_chunks;" if self._vec else "")
        )
        self.db.commit()

    def commit(self) -> None:
        self.db.commit()

    # --- search -------------------------------------------------------------

    def search(
        self, query: str, kind: str | None = None, project: str | None = None,
        lang: str | None = None, top_k: int = 8,
    ) -> list[SearchResult]:
        pool = max(top_k * 6, 40)
        fts = self._fts_search(query, pool)
        vec = self._vector_search(query, pool)
        fused = _rrf([fts, vec])
        results: list[SearchResult] = []
        for chunk_id, score in fused:
            row = self.db.execute("SELECT * FROM chunks WHERE chunk_id=?", (chunk_id,)).fetchone()
            if row is None:
                continue
            if kind and row["kind"] != kind:
                continue
            if project and row["project"] != project:
                continue
            if lang and (row["lang"] or "") != lang:
                continue
            results.append(self._to_result(row, score))
            if len(results) >= top_k:
                break
        return results

    def _fts_search(self, query: str, limit: int) -> list[tuple[str, float]]:
        toks = _FTS_TOKEN_RE.findall(query)
        if not toks:
            return []
        match = " OR ".join(f'"{t}"' for t in toks)
        try:
            cur = self.db.execute(
                "SELECT chunk_id, bm25(chunks_fts) AS rank FROM chunks_fts "
                "WHERE chunks_fts MATCH ? ORDER BY rank LIMIT ?",
                (match, limit),
            )
            return [(r["chunk_id"], r["rank"]) for r in cur.fetchall()]
        except sqlite3.OperationalError:
            return []

    def _vector_search(self, query: str, limit: int) -> list[tuple[str, float]]:
        from .embed import Embedder

        qv = Embedder(self.settings.model_name, self.dim).embed_one(query)
        if self._vec:
            try:
                blob = array.array("f", qv).tobytes()
                cur = self.db.execute(
                    "SELECT c.chunk_id AS chunk_id, v.distance AS distance "
                    "FROM vec_chunks v JOIN chunks c ON c.rowid = v.rowid "
                    "WHERE v.embedding MATCH ? AND k = ? ORDER BY v.distance",
                    (blob, limit),
                )
                return [(r["chunk_id"], r["distance"]) for r in cur.fetchall()]
            except sqlite3.OperationalError:
                pass
        # brute force cosine
        scored: list[tuple[str, float]] = []
        cur = self.db.execute("SELECT chunk_id, embedding FROM chunks")
        for r in cur.fetchall():
            vec = array.array("f")
            vec.frombytes(r["embedding"])
            scored.append((r["chunk_id"], -_cosine(qv, vec)))  # negative => sorts asc like distance
        scored.sort(key=lambda x: x[1])
        return scored[:limit]

    def _to_result(self, row: sqlite3.Row, score: float) -> SearchResult:
        return SearchResult(
            score=score, project=row["project"], source=row["source"], kind=row["kind"],
            lang=row["lang"], path=row["path"], title=row["title"], text=row["text"],
            start_line=row["start_line"], end_line=row["end_line"], url=row["url"],
            license=row["license"], tags=json.loads(row["tags"] or "{}"),
        )

    # --- protocol / patch helpers ------------------------------------------

    def list_protocols(self, family: str | None = None, stability: str | None = None) -> list[dict]:
        cur = self.db.execute(
            "SELECT DISTINCT json_extract(tags,'$.protocol') AS protocol, "
            "json_extract(tags,'$.stability') AS stability, source "
            "FROM chunks WHERE kind='protocol' AND protocol IS NOT NULL"
        )
        out = []
        for r in cur.fetchall():
            if stability and (r["stability"] or "") != stability:
                continue
            out.append({"protocol": r["protocol"], "stability": r["stability"], "source": r["source"]})
        if family:
            out = [o for o in out if (o["stability"] or "") == family]
        return sorted(out, key=lambda o: (o["stability"] or "", o["protocol"]))

    def get_protocol(self, name: str) -> list[SearchResult]:
        cur = self.db.execute(
            "SELECT * FROM chunks WHERE kind='protocol' AND "
            "(json_extract(tags,'$.protocol')=? OR title=?) ORDER BY title",
            (name, name),
        )
        return [self._to_result(r, 0.0) for r in cur.fetchall()]

    def kind_rows(self, kind: str) -> list[sqlite3.Row]:
        return self.db.execute("SELECT * FROM chunks WHERE kind=?", (kind,)).fetchall()

    # --- stats --------------------------------------------------------------

    def stats(self) -> dict:
        total = self.db.execute("SELECT COUNT(*) AS c FROM chunks").fetchone()["c"]
        by_kind = {
            r["kind"]: r["c"]
            for r in self.db.execute("SELECT kind, COUNT(*) AS c FROM chunks GROUP BY kind").fetchall()
        }
        by_project = {
            r["project"]: r["c"]
            for r in self.db.execute(
                "SELECT project, COUNT(*) AS c FROM chunks GROUP BY project"
            ).fetchall()
        }
        return {
            "chunks": total,
            "by_kind": by_kind,
            "by_project": by_project,
            "vector_backend": "sqlite-vec" if self._vec else "bruteforce",
        }


def _cosine(a: list[float], b: array.array) -> float:
    n = min(len(a), len(b))
    dot = sum(a[i] * b[i] for i in range(n))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(b[i] * b[i] for i in range(n))) or 1.0
    return dot / (na * nb)


def _rrf(rankings: list[list[tuple[str, float]]], k: int = 60) -> list[tuple[str, float]]:
    """Reciprocal rank fusion over multiple ranked id lists (lower input = better)."""
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, (cid, _score) in enumerate(ranking):
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


__all__ = ["Store", "SearchResult", "Path"]
