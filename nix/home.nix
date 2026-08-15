# Home-manager module: install wwn-mcp on PATH (stdio MCP for any host).
# Cursor uses mcpServers; Zed uses context_servers — same command/args payload.
self:
{ config, lib, pkgs, ... }:

let
  cfg = config.programs.wwn-mcp;
  defaultPackage = self.packages.${pkgs.stdenv.hostPlatform.system}.wwn-mcp;
  dataDir = cfg.dataDir;
  corpusToml = cfg.corpusManifest;
in
{
  options.programs.wwn-mcp = {
    enable = lib.mkEnableOption "WWN-MCP stdio RAG server on PATH";

    package = lib.mkOption {
      type = lib.types.package;
      default = defaultPackage;
      description = "The wwn-mcp package to install.";
    };

    dataDir = lib.mkOption {
      type = lib.types.str;
      default = "${config.home.homeDirectory}/.local/share/wwn-mcp";
      description = "Runtime data dir (corpus cache + sqlite index).";
    };

    corpusManifest = lib.mkOption {
      type = lib.types.str;
      default = "${self}/corpus.toml";
      description = "Path to corpus.toml (local siblings + git fallbacks). Prefer a live checkout path so ../wwn-* siblings resolve.";
    };

    model = lib.mkOption {
      type = lib.types.str;
      default = "BAAI/bge-small-en-v1.5";
      description = "Embedding model name (fastembed). Falls back to hashing if unavailable.";
    };

    reindex = {
      enable = lib.mkOption {
        type = lib.types.bool;
        default = true;
        description = "Install a user timer that periodically fetch+index the corpus.";
      };
      onCalendar = lib.mkOption {
        type = lib.types.str;
        default = "daily";
        description = "systemd OnCalendar schedule for reindexing (Linux; ignored on Darwin).";
      };
    };
  };

  config = lib.mkIf cfg.enable {
    home.packages = [ cfg.package ];

    home.sessionVariables = {
      WWN_MCP_DATA_DIR = dataDir;
      WWN_MCP_CORPUS_TOML = corpusToml;
      WWN_MCP_MODEL = cfg.model;
      FASTEMBED_CACHE_PATH = "${dataDir}/models";
    };

    # Linux user systemd timer. On Darwin, reindex via launchd or manual
    # `wwn-mcp fetch && wwn-mcp index` / nh switch oneshot.
    systemd.user.services.wwn-mcp-reindex = lib.mkIf (cfg.reindex.enable && pkgs.stdenv.isLinux) {
      Unit.Description = "WWN-MCP corpus re-fetch + re-index";
      Service = {
        Type = "oneshot";
        Environment = [
          "WWN_MCP_DATA_DIR=${dataDir}"
          "WWN_MCP_CORPUS_TOML=${corpusToml}"
          "WWN_MCP_CORPUS_DIR=${dataDir}/corpus"
          "WWN_MCP_MODEL=${cfg.model}"
          "FASTEMBED_CACHE_PATH=${dataDir}/models"
        ];
        ExecStart = pkgs.writeShellScript "wwn-mcp-reindex" ''
          set -euo pipefail
          mkdir -p "${dataDir}"
          export WWN_MCP_DB="${dataDir}/index.build.sqlite"
          ${cfg.package}/bin/wwn-mcp fetch
          ${cfg.package}/bin/wwn-mcp index --reset
          mv -f "${dataDir}/index.build.sqlite" "${dataDir}/index.sqlite"
        '';
      };
    };

    systemd.user.timers.wwn-mcp-reindex = lib.mkIf (cfg.reindex.enable && pkgs.stdenv.isLinux) {
      Unit.Description = "WWN-MCP reindex timer";
      Timer = {
        OnCalendar = cfg.reindex.onCalendar;
        Persistent = true;
        RandomizedDelaySec = "30m";
      };
      Install.WantedBy = [ "timers.target" ];
    };
  };
}
