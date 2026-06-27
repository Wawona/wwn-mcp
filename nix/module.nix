self:
{ config, lib, pkgs, ... }:

let
  cfg = config.services.wwn-mcp;
  defaultPackage = self.packages.${pkgs.stdenv.hostPlatform.system}.wwn-mcp;

  reindexScript = pkgs.writeShellScript "wwn-mcp-reindex" ''
    set -euo pipefail
    export WWN_MCP_DATA_DIR=${cfg.dataDir}
    export WWN_MCP_CORPUS_TOML=${cfg.corpusManifest}
    export WWN_MCP_CORPUS_DIR=${cfg.dataDir}/corpus
    export WWN_MCP_MODEL=${cfg.model}
    # Build into a staging DB then atomically swap so `serve` never reads a
    # half-written index.
    export WWN_MCP_DB=${cfg.dataDir}/index.build.sqlite
    ${cfg.package}/bin/wwn-mcp fetch
    ${cfg.package}/bin/wwn-mcp index --reset
    mv -f ${cfg.dataDir}/index.build.sqlite ${cfg.dataDir}/index.sqlite
    ${pkgs.systemd}/bin/systemctl try-restart wwn-mcp.service || true
  '';
in
{
  options.services.wwn-mcp = {
    enable = lib.mkEnableOption "WWN-MCP RAG + MCP server";

    package = lib.mkOption {
      type = lib.types.package;
      default = defaultPackage;
      description = "The wwn-mcp package to run.";
    };

    domain = lib.mkOption {
      type = lib.types.str;
      default = "mcp.wawona.io";
      description = "Public hostname served over TLS by the reverse proxy.";
    };

    host = lib.mkOption {
      type = lib.types.str;
      default = "127.0.0.1";
      description = "Address the MCP server binds (kept local; TLS at the proxy).";
    };

    port = lib.mkOption {
      type = lib.types.port;
      default = 8765;
      description = "Local port for the MCP Streamable HTTP server.";
    };

    dataDir = lib.mkOption {
      type = lib.types.path;
      default = "/var/lib/wwn-mcp";
      description = "Runtime data dir (corpus cache + sqlite index).";
    };

    corpusManifest = lib.mkOption {
      type = lib.types.path;
      default = "${self}/corpus.toml";
      description = ''
        Path to corpus.toml. On a server, point this at a manifest whose
        `wawona` source is a git entry (the bundled default uses a local
        `../Wawona` path meant for dev).
      '';
    };

    model = lib.mkOption {
      type = lib.types.str;
      default = "BAAI/bge-small-en-v1.5";
      description = "Embedding model name (fastembed). Falls back to hashing if unavailable.";
    };

    tokenFile = lib.mkOption {
      type = lib.types.nullOr lib.types.path;
      default = null;
      description = ''
        File containing `WWN_MCP_TOKEN=<bearer>` used by the reverse proxy to
        require `Authorization: Bearer <token>`. If null, the proxy allows all
        (use only behind another auth layer).
      '';
    };

    reindex = {
      enable = lib.mkOption {
        type = lib.types.bool;
        default = true;
        description = "Periodically re-fetch + re-index with an atomic DB swap.";
      };
      onCalendar = lib.mkOption {
        type = lib.types.str;
        default = "daily";
        description = "systemd OnCalendar schedule for reindexing.";
      };
    };

    proxy.enable = lib.mkOption {
      type = lib.types.bool;
      default = true;
      description = "Run a Caddy reverse proxy terminating TLS at `domain` with Bearer auth.";
    };

    nixos = {
      enable = lib.mkOption {
        type = lib.types.bool;
        default = true;
        description = ''
          Co-host MCP-NixOS (utensils/mcp-nixos) as a companion MCP server so
          models get accurate, live Nix knowledge (nixpkgs packages/options,
          nix-darwin, home-manager, flakes, noogle, binary-cache status).
        '';
      };
      package = lib.mkOption {
        type = lib.types.package;
        default = self.inputs.mcp-nixos.packages.${pkgs.stdenv.hostPlatform.system}.default;
        defaultText = lib.literalExpression "inputs.mcp-nixos.packages.\${system}.default";
        description = "The mcp-nixos package to run.";
      };
      port = lib.mkOption {
        type = lib.types.port;
        default = 8001;
        description = "Local port for the companion MCP-NixOS HTTP server.";
      };
      path = lib.mkOption {
        type = lib.types.str;
        default = "/nixos/mcp";
        description = "HTTP MCP endpoint path for the companion server (served under `domain`).";
      };
    };
  };

  config = lib.mkIf cfg.enable {
    systemd.services.wwn-mcp = {
      description = "WWN-MCP MCP server";
      wantedBy = [ "multi-user.target" ];
      after = [ "network-online.target" ];
      wants = [ "network-online.target" ];
      environment = {
        WWN_MCP_DATA_DIR = cfg.dataDir;
        WWN_MCP_CORPUS_TOML = cfg.corpusManifest;
        WWN_MCP_CORPUS_DIR = "${cfg.dataDir}/corpus";
        WWN_MCP_DB = "${cfg.dataDir}/index.sqlite";
        WWN_MCP_MODEL = cfg.model;
        WWN_MCP_HOST = cfg.host;
        WWN_MCP_PORT = toString cfg.port;
        FASTEMBED_CACHE_PATH = "${cfg.dataDir}/models";
      };
      serviceConfig = {
        ExecStart = "${cfg.package}/bin/wwn-mcp serve --host ${cfg.host} --port ${toString cfg.port} --transport http";
        Restart = "on-failure";
        RestartSec = 3;
        # Hardening
        DynamicUser = true;
        StateDirectory = "wwn-mcp";
        WorkingDirectory = cfg.dataDir;
        NoNewPrivileges = true;
        ProtectSystem = "strict";
        ProtectHome = true;
        PrivateTmp = true;
        PrivateDevices = true;
        ProtectKernelTunables = true;
        ProtectKernelModules = true;
        ProtectControlGroups = true;
        RestrictAddressFamilies = [ "AF_INET" "AF_INET6" "AF_UNIX" ];
        RestrictNamespaces = true;
        LockPersonality = true;
        MemoryDenyWriteExecute = false; # onnxruntime may JIT
        SystemCallFilter = [ "@system-service" ];
        ReadWritePaths = [ cfg.dataDir ];
      };
    };

    systemd.services.wwn-mcp-reindex = lib.mkIf cfg.reindex.enable {
      description = "WWN-MCP corpus re-fetch + re-index (atomic swap)";
      after = [ "network-online.target" ];
      wants = [ "network-online.target" ];
      path = [ pkgs.git pkgs.openssh ];
      serviceConfig = {
        Type = "oneshot";
        ExecStart = reindexScript;
        DynamicUser = true;
        StateDirectory = "wwn-mcp";
        WorkingDirectory = cfg.dataDir;
        ReadWritePaths = [ cfg.dataDir ];
      };
    };

    systemd.timers.wwn-mcp-reindex = lib.mkIf cfg.reindex.enable {
      wantedBy = [ "timers.target" ];
      timerConfig = {
        OnCalendar = cfg.reindex.onCalendar;
        Persistent = true;
        RandomizedDelaySec = "30m";
      };
    };

    # Companion MCP-NixOS server: accurate, live Nix knowledge (packages,
    # options, nix-darwin, home-manager, flakes, noogle, binary-cache status).
    systemd.services.mcp-nixos = lib.mkIf cfg.nixos.enable {
      description = "MCP-NixOS companion server (utensils/mcp-nixos)";
      wantedBy = [ "multi-user.target" ];
      after = [ "network-online.target" ];
      wants = [ "network-online.target" ];
      environment = {
        MCP_NIXOS_TRANSPORT = "http";
        MCP_NIXOS_HOST = cfg.host;
        MCP_NIXOS_PORT = toString cfg.nixos.port;
        MCP_NIXOS_PATH = cfg.nixos.path;
        MCP_NIXOS_STATELESS_HTTP = "1";
        MCP_NIXOS_CACHE_DIR = "/var/lib/mcp-nixos";
      };
      serviceConfig = {
        ExecStart = "${cfg.nixos.package}/bin/mcp-nixos";
        Restart = "on-failure";
        RestartSec = 3;
        DynamicUser = true;
        StateDirectory = "mcp-nixos";
        NoNewPrivileges = true;
        ProtectSystem = "strict";
        ProtectHome = true;
        PrivateTmp = true;
        ProtectKernelTunables = true;
        ProtectKernelModules = true;
        ProtectControlGroups = true;
        RestrictAddressFamilies = [ "AF_INET" "AF_INET6" "AF_UNIX" ];
        RestrictNamespaces = true;
        LockPersonality = true;
        SystemCallFilter = [ "@system-service" ];
        ReadWritePaths = [ "/var/lib/mcp-nixos" ];
      };
    };

    services.caddy = lib.mkIf cfg.proxy.enable {
      enable = lib.mkDefault true;
      virtualHosts.${cfg.domain}.extraConfig =
        (lib.optionalString (cfg.tokenFile != null) ''
          @noauth not header Authorization "Bearer {$WWN_MCP_TOKEN}"
          respond @noauth "Unauthorized" 401
        '')
        + (lib.optionalString cfg.nixos.enable ''
          handle ${cfg.nixos.path}* {
            reverse_proxy ${cfg.host}:${toString cfg.nixos.port}
          }
        '')
        + ''
          handle {
            reverse_proxy ${cfg.host}:${toString cfg.port}
          }
        '';
    };

    systemd.services.caddy.serviceConfig.EnvironmentFile =
      lib.mkIf (cfg.proxy.enable && cfg.tokenFile != null) cfg.tokenFile;
  };
}
