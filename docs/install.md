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

The same install contract must support an ERP host, one or more mirror
hosts (cluster members), and a separate WordPress/WooCommerce
storefront host that may be managed elsewhere, including by a hosting
provider.

The current proof installation maps those roles to `kuche.aprp.store`,
`kotka.aprp.store`, and `aprp.store`.
The repo-owned config seeds the standardized container names
`aprp-server` and `aprp-mirror`.

The install path must not hardcode deployment hosts or public URLs in
compose files or shell scripts. The repo-owned config renderer translates
the tracked YAML into the shell exports the runtime uses.

Public TLS certificates should be issued with DNS-01 ACME per hostname
using certbot and manual TXT records. See `docs/system.md` for the
issuance procedure.

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
2. fill the instance-specific ERP host, mirror hosts, storefront host,
   and local runtime settings;
3. keep secrets in the untracked env files;
4. render the shell exports with `python3 ops/opsconfig.py primary`;
5. issue DNS-01 certificates for `kuche.aprp.store` and
   `kotka.aprp.store` with certbot and manual TXT records through
   Superhosting.bg;
6. run `./ops/deploy.sh` on the ERP host;
7. run `./ops/deploy_mirror.sh` on each mirror host when present;
8. connect the storefront host to APRP and verify the storefront
   contract;
9. run `./ops/backup.sh backup` after the site is up.

## Validation

- `bash -n` must pass for the repo-owned shell scripts;
- `docker compose -f compose.yaml config` must pass when Docker is
  available;
- `./ops/db_mirror_restore.sh cluster-status` must report a healthy
  primary cluster when the stack is live;
- the local installation should not require hardcoded production hosts
  in non-config files.
