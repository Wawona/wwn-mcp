{
  description = "WWN-MCP: local-embeddings RAG + stdio MCP server for the Wawona stack.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    let
      # Pinned embedding model for hermetic, offline-capable embeds.
      # NOTE: build with `nix build .#wwn-mcp-model` once and replace the hash
      # below with the value Nix reports (standard fakeHash workflow). The model
      # is NOT a build input of the package, so `nix flake check` / `nix build
      # .#wwn-mcp` do not require it.
      modelInfo = {
        name = "bge-small-en-v1.5";
        url = "https://huggingface.co/qdrant/bge-small-en-v1.5-onnx-q/resolve/main/model_optimized.onnx";
        hash = nixpkgs.lib.fakeHash;
      };

      perSystem = flake-utils.lib.eachDefaultSystem (system:
        let
          pkgs = import nixpkgs { inherit system; };
          lib = pkgs.lib;
          py = pkgs.python3Packages;

          # Optional runtime deps: present in nixpkgs on most channels, but the
          # package degrades gracefully (hashing embedder / brute-force search)
          # when absent, so we include them only if available.
          optionalDeps = lib.filter (x: x != null) [
            (py.mcp or null)
            (py.fastembed or null)
            (py.sqlite-vec or null)
          ];

          wwn-mcp = py.buildPythonApplication {
            pname = "wwn-mcp";
            version = "0.2.1";
            src = self;
            pyproject = true;
            build-system = [ py.setuptools ];
            dependencies = optionalDeps;
            # Tests need writable data dir; run via checks.pytest outside sandbox.
            doCheck = false;
            pythonImportsCheck = [
              "wwn_mcp"
              "wwn_mcp.cli"
              "wwn_mcp.embed"
              "wwn_mcp.store"
              "wwn_mcp.contribute"
            ];
            # Bundle the corpus manifest + knowledge next to the package so an
            # installed (read-only store) wwn-mcp finds them with no env override.
            postInstall = ''
              install -Dm644 corpus.toml \
                "$out/${py.python.sitePackages}/wwn_mcp/corpus.toml"
              mkdir -p "$out/${py.python.sitePackages}/wwn_mcp/knowledge"
              cp -R knowledge/. "$out/${py.python.sitePackages}/wwn_mcp/knowledge/"
            '';
            meta = {
              description = "Local-embeddings RAG + stdio MCP server for the Wawona stack.";
              homepage = "https://github.com/Wawona/WWN-MCP";
              license = lib.licenses.mit;
              mainProgram = "wwn-mcp";
            };
          };

          wwn-mcp-model = pkgs.fetchurl {
            name = "wwn-mcp-${modelInfo.name}.onnx";
            url = modelInfo.url;
            hash = modelInfo.hash;
          };

          pytestCheck = pkgs.runCommand "wwn-mcp-pytest" {
            nativeBuildInputs = [
              (pkgs.python3.withPackages (ps:
                [ ps.pytest ps.setuptools ]
                ++ lib.filter (x: x != null) [
                  (ps.mcp or null)
                  (ps.fastembed or null)
                  (ps.sqlite-vec or null)
                ]))
            ];
          } ''
            cp -R ${self} srcdir
            chmod -R u+w srcdir
            cd srcdir
            export PYTHONPATH="$PWD/src:$PYTHONPATH"
            pytest -q
            touch $out
          '';
        in
        {
          packages = {
            inherit wwn-mcp wwn-mcp-model;
            default = wwn-mcp;
          };

          checks = {
            package = wwn-mcp;
            pytest = pytestCheck;
          };

          apps = {
            wwn-mcp = {
              type = "app";
              program = "${wwn-mcp}/bin/wwn-mcp";
            };
            default = self.apps.${system}.wwn-mcp;
          };

          devShells.default = pkgs.mkShell {
            packages = [
              (pkgs.python3.withPackages (ps:
                [ ps.setuptools ps.pip ]
                ++ lib.filter (x: x != null) [
                  (ps.mcp or null)
                  (ps.fastembed or null)
                  (ps.sqlite-vec or null)
                  (ps.pytest or null)
                  (ps.ruff or null)
                ]))
              pkgs.git
            ];
            shellHook = ''
              export PYTHONPATH="$PWD/src:$PYTHONPATH"
              echo "wwn-mcp dev shell (stdio). Try: python -m wwn_mcp.cli info"
            '';
          };
        });
    in
    perSystem // {
      # home-manager: programs.wwn-mcp.enable = true;
      homeModules.wwn-mcp = import ./nix/home.nix self;
      homeModules.default = self.homeModules.wwn-mcp;

      overlays.default = final: prev: {
        wwn-mcp = self.packages.${prev.stdenv.hostPlatform.system}.wwn-mcp;
      };
    };
}
