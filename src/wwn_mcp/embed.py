"""Text embeddings.

Primary backend is ``fastembed`` (ONNX CPU, BGE-small, no torch). When it is
not installed, WWN-MCP transparently falls back to a deterministic hashing
embedder so the pipeline always runs (tests, constrained hosts). The Nix
package installs fastembed for real semantic quality.
"""

from __future__ import annotations

import hashlib
import math
import re

_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


class Embedder:
    def __init__(self, model_name: str, dim: int) -> None:
        self.model_name = model_name
        self.dim = dim
        self._backend = "hashing"
        self._model = None
        self._try_fastembed()

    def _try_fastembed(self) -> None:
        try:
            from fastembed import TextEmbedding  # type: ignore

            self._model = TextEmbedding(model_name=self.model_name)
            self._backend = "fastembed"
        except Exception:  # noqa: BLE001 - fall back silently
            self._model = None
            self._backend = "hashing"

    @property
    def backend(self) -> str:
        return self._backend

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        if self._backend == "fastembed" and self._model is not None:
            try:
                return [list(map(float, v)) for v in self._model.embed(texts)]
            except Exception:  # noqa: BLE001 - degrade to hashing on runtime error
                self._backend = "hashing"
        return [self._hash_embed(t) for t in texts]

    def embed_one(self, text: str) -> list[float]:
        return self.embed([text])[0]

    def _hash_embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for tok in _TOKEN_RE.findall(text.lower()):
            h = int(hashlib.md5(tok.encode()).hexdigest(), 16)  # noqa: S324 - not security
            idx = h % self.dim
            sign = 1.0 if (h >> 8) & 1 else -1.0
            vec[idx] += sign
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]
