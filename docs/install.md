# Install
**Doc ID:** INSTALL
**Doc Type:** operator-guide
**Project Version:** 0.4.0
**DevCovenant Version:** 1.0.1b5

## Overview

APRP installs as an ERPNext/Frappe application plus repo-owned operator
scripts. The install is config-first: `ops/opsconfig.yaml` holds the
non-secret runtime shape, while `ops/env.primary.example` and
`ops/env.mirror.example` hold secrets and local auth.

The install path must not hardcode deployment hosts or public URLs in
compose files or shell scripts. The repo-owned config renderer translates
the tracked YAML into the shell exports the runtime uses.

For runtime details, see `docs/system.md`. For controlled public demo
rules, see `docs/showcase.md` and `docs/security.md`.

## Prerequisites

- an ERPNext/Frappe bench or containerized host;
- the tracked `ops/opsconfig.yaml.example` file;
- a local `ops/opsconfig.yaml` instance copy;
- the secret env files for the target host;
- Docker when you want to validate the Compose render locally.

## Install steps

1. copy `ops/opsconfig.yaml.example` to `ops/opsconfig.yaml`;
2. fill the instance-specific hostnames and local runtime settings;
3. keep secrets in the untracked env files;
4. render the shell exports with `python3 ops/opsconfig.py primary`;
5. run `./ops/deploy.sh` on the primary host;
6. run `./ops/deploy_mirror.sh` on the mirror host when present;
7. run `./ops/backup.sh backup` after the site is up.

## Validation

- `bash -n` must pass for the repo-owned shell scripts;
- `docker compose -f compose.yaml config` must pass when Docker is
  available;
- `./ops/db_mirror_restore.sh cluster-status` must report a healthy
  primary cluster when the stack is live;
- the local installation should not require hardcoded production hosts
  in non-config files.
