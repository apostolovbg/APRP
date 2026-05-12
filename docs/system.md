# System Guide
**Doc ID:** SYSTEM
**Doc Type:** operator-guide
**Project Version:** 0.4.0
**DevCovenant Version:** 1.0.1b5

## Overview

APRP runs as a containerized ERPNext/Frappe stack with a Galera/ProxySQL
database layout.

The primary ERP/backend host is `kuche.aprp.store`.
The mirror database member is `kotka.aprp.store`.
The public APRP showcase domain is `aprp.store`.

## Primary host

The primary host runs the ERP runtime, workers, Redis, ProxySQL, Galera
primary, and the arbitrator service.

Bring the stack up with:

```bash
docker compose --env-file .env.primary up -d --build
```

The repo-owned deploy command performs the same sequence and then prepares the
site:

```bash
./ops/deploy.sh
```

## Mirror host

The mirror host runs only the Galera mirror member.

Bring it up with:

```bash
docker compose --env-file .env.mirror -f compose.mirror.yaml up -d
```

Mirror maintenance uses:

```bash
./ops/deploy_mirror.sh
./ops/db_mirror_restore.sh mirror-status
```

## Site bootstrap

The site bootstrap helper creates the site when missing, updates the runtime
database and Redis settings, and installs `erpnext` plus the APRP app.

Run it from the backend container or through deploy:

```bash
./ops/site_setup.sh
```

The expected site name on the primary host is `kuche.aprp.store`.

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

## Recovery

Use the mirror only as a database continuity layer.
Backups still handle file recovery, site configuration recovery, and full
restore workflows.

When a recovery happens:

1. restore the database or session bundle;
2. restore `site_config.json` and `common_site_config.json`;
3. run `bench --site kuche.aprp.store migrate`;
4. bring the primary services back up;
5. verify the public host responses.
