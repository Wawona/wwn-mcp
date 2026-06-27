{
  description = "WWN-MCP: local-embeddings RAG + MCP server for the Wawona stack.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";

    # WWN-MCP depends on MCP-NixOS (utensils/mcp-nixos) so models get accurate,
    # real-time Nix knowledge (nixpkgs packages/options, nix-darwin,
    # home-manager, flakes, noogle, binary-cache status). It is co-hosted as a
    # companion MCP server by the NixOS module; it is a *live* MCP, not part of
    # WWN-MCP's indexed RAG corpus.
    mcp-nixos.url = "github:utensils/mcp-nixos";
    mcp-nixos.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils, mcp-nixos }:
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
            version = "0.1.0";
            src = self;
            pyproject = true;
            build-system = [ py.setuptools ];
            dependencies = optionalDeps;
            # Tests need network/model; skip in the sandbox.
            doCheck = false;
            pythonImportsCheck = [ "wwn_mcp" "wwn_mcp.cli" ];
            # Bundle the corpus manifest next to the package so an installed
            # (read-only store) wwn-mcp finds it with no WWN_MCP_CORPUS_TOML env.
            postInstall = ''
              install -Dm644 corpus.toml \
                "$out/${py.python.sitePackages}/wwn_mcp/corpus.toml"
            '';
            meta = {
              description = "Local-embeddings RAG + MCP server for the Wawona stack.";
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
        in
        {
          packages = {
            inherit wwn-mcp wwn-mcp-model;
            default = wwn-mcp;
            # Companion server, re-exported for convenience / co-hosting.
            mcp-nixos = mcp-nixos.packages.${system}.default;
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
              pkgs.caddy
            ];
            shellHook = ''
              export PYTHONPATH="$PWD/src:$PYTHONPATH"
              echo "wwn-mcp dev shell. Try: python -m wwn_mcp.cli info"
            '';
          };
        });
    in
    perSystem // {
      # System-independent NixOS module (defined in ./nix/module.nix).
      nixosModules.wwn-mcp = import ./nix/module.nix self;
      nixosModules.default = self.nixosModules.wwn-mcp;

      overlays.default = final: prev: {
        wwn-mcp = self.packages.${prev.stdenv.hostPlatform.system}.wwn-mcp;
      };
    };
}
