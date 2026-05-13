# System Guide
**Doc ID:** SYSTEM
**Doc Type:** operator-guide
**Project Version:** 0.4.0
**DevCovenant Version:** 1.0.1b5

## Overview

APRP runs as a containerized ERPNext/Frappe stack with a Galera/ProxySQL
database layout.

All non-secret runtime configuration lives in `ops/opsconfig.yaml`.
The repo-owned scripts translate that file into the shell environment they
need before they call Compose or the backup tools.
That YAML file also carries the internal service hostnames, ports, and
URLs used by the stack bootstrap.

The tracked `ops/opsconfig.yaml.example` file shows the expected shape of
that instance config.

The `ops/env.primary.example` and `ops/env.mirror.example` files are for
secrets and machine-local auth only.

## Primary host

The primary host runs the ERP runtime, workers, Redis, ProxySQL, Galera
primary, and the arbitrator service.

The backend container starts through `ops/backend_entrypoint.sh`, which runs
`ops/site_setup.sh` before it hands off to `bench serve`.

The startup path reads the instance config shape through the repo-owned
operator files, not through a hardcoded host list.

Bring the stack up through the repo-owned deploy script:

```bash
./ops/deploy.sh
```

The deploy script loads `ops/opsconfig.yaml`, exports the non-secret config,
and then prepares the site.

## Mirror host

The mirror host runs only the Galera mirror member.

The mirror stack keeps its own `db-mirror-data` volume and `mirror-net`
network. It does not publish ERP ports or run ERP services.

Bring it up with:

```bash
./ops/deploy_mirror.sh
```

Mirror maintenance uses:

```bash
./ops/db_mirror_restore.sh mirror-status
./ops/db_mirror_restore.sh mirror-reseed
./ops/db_mirror_restore.sh mirror-rejoin
```

## Site bootstrap

The site bootstrap helper creates the site when missing, updates the runtime
database and Redis settings, and installs `erpnext` plus the APRP app.

The same helper is used by the backend startup path and by deploy so fresh
local and deployed stacks converge on the same site contract.

Run it from the backend container or through deploy:

```bash
./ops/site_setup.sh
```

The expected site name on the primary host comes from `ops/opsconfig.yaml`
through the repo-owned config loader.

## Backup

Backups run from the backend container and capture database state, site files,
private files, and site configuration.

Run a local backup with:

```bash
./ops/backup.sh backup
```

Restore from a local session, a single SQL file, or an offsite session with:

```bash
./ops/backup.sh restore [SESSION_DIR|SQL_FILE|REMOTE_SESSION]
```

## Automation wrappers

`ops/render_workflows.py` generates the non-CI GitHub workflow wrappers
under `.github/workflows/`.

The generated wrappers are thin entrypoints for self-hosted runners or
host-managed checkouts. They call the repo-owned deploy, backup, mirror,
and recovery scripts directly. `ci.yml` remains DevCovenant-managed.

## Recovery

Use the mirror only as a database continuity layer.
Backups still handle file recovery, site configuration recovery, and full
restore workflows.

Mirror recovery is separate from site recovery.

Use this sequence for mirror rebuilds:

1. run `./ops/db_mirror_restore.sh mirror-restore` when the mirror needs a
   backup-based restore;
2. run `./ops/db_mirror_restore.sh mirror-reseed` when the mirror datadir must
   be recreated from scratch;
3. run `./ops/db_mirror_restore.sh mirror-rejoin` after the mirror comes back;
4. verify `./ops/db_mirror_restore.sh mirror-status` reports wsrep ready.

When a recovery happens:

1. restore the database or session bundle;
2. restore `site_config.json` and `common_site_config.json`;
3. run `bench --site <backend site name from ops/opsconfig.yaml> migrate`;
4. bring the primary services back up;
5. verify the backend host responses.
