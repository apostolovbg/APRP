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

The same config shape can describe an ERP host, one or more mirror
hosts (cluster members), and an external storefront host on another
server or provider. The runtime contract stays the same whether those
roles are co-located or separated.

The current proof installation maps the ERP host to `kuche.aprp.store`,
the mirror host to `kotka.aprp.store`, and the storefront host to
`aprp.store`.
The repo-owned scripts seed the standardized container names
`aprp-server` and `aprp-mirror` from tracked config.

Run the repo-owned scripts from the APRP checkout root.

A WordPress/WooCommerce site on any server can connect to APRP on any
other server through the storefront contract.

The tracked `ops/opsconfig.yaml.example` file shows the expected shape of
that instance config.

The `ops/env.primary.example` and `ops/env.mirror.example` files are for
secrets and machine-local auth only.

Public TLS certificates are issued per hostname with DNS-01 ACME. The
hostnames may point at the same public IP or at different hosts; the
certificate workflow stays the same.

Local certbot state lives in untracked `ops/certs/<hostname>/`
directories inside the checkout root. Each hostname keeps its own
`config-dir`, `work-dir`, and `logs-dir`.

For install and development guidance, see `docs/install.md` and
`docs/development.md`. For security and public-demo rules, see
`docs/security.md`.

## ERP host

The ERP host runs the ERP runtime, workers, Redis, ProxySQL, the Galera
primary member, and the arbitrator service.

In the current proof installation, this role maps to
`kuche.aprp.store` and the `aprp-server` container.

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

## Mirror hosts

The mirror hosts run the Galera mirror members.

In the current proof installation, this role maps to
`kotka.aprp.store` and the `aprp-mirror` container.

The mirror stack keeps its own `db-mirror-data` volume and `mirror-net`
network. It does not publish ERP ports or run ERP services.

The mirror profile may be co-located with the primary profile during a
proof install. When it is, the profile still behaves like an agnostic
mirror: it uses the mirror config, the mirror data, and the mirror
scripts.

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

The expected site name on the ERP host comes from `ops/opsconfig.yaml`
through the repo-owned config loader.

## Storefront host

The storefront host is the public WordPress/WooCommerce surface or a
compatible external sales surface.

It may be managed by the operator, by a hosting provider, or by a
separate team. APRP still connects to it through the storefront
contract.

The storefront host may share infrastructure with the ERP host during a
proof install, but it does not become the ERP authority.

In the current proof installation, this role maps to `aprp.store`.

## DNS-01 Certificate Issuance

Use DNS-01 when issuing public TLS certificates for APRP hosts.

This works for the ERP host, each mirror host in the cluster, the
storefront host, and any other operator-owned domain.

The current proof installation uses Superhosting.bg as the DNS provider
for the ERP and mirror hostnames.

From the APRP checkout root, run:

```bash
mkdir -p ops/certs/kuche.aprp.store
certbot certonly \
  --manual \
  --preferred-challenges dns \
  --agree-tos \
  --email ops@example.invalid \
  --config-dir ops/certs/kuche.aprp.store \
  --work-dir ops/certs/kuche.aprp.store/work \
  --logs-dir ops/certs/kuche.aprp.store/logs \
  -d kuche.aprp.store

mkdir -p ops/certs/kotka.aprp.store
certbot certonly \
  --manual \
  --preferred-challenges dns \
  --agree-tos \
  --email ops@example.invalid \
  --config-dir ops/certs/kotka.aprp.store \
  --work-dir ops/certs/kotka.aprp.store/work \
  --logs-dir ops/certs/kotka.aprp.store/logs \
  -d kotka.aprp.store
```

Procedure:

1. pick the hostname or hostnames you want to publish;
2. ensure the DNS zone is under operator control;
3. install `certbot` or another ACME client that supports DNS-01
   validation;
4. store the DNS provider token or manual DNS credentials in an
   untracked secret file;
5. request a certificate for the chosen hostname;
6. create the `_acme-challenge` TXT record manually or through the DNS
   provider API;
7. wait for propagation and finalize issuance;
8. install the certificate and private key in the reverse proxy;
9. reload the proxy;
10. repeat for each hostname or operator-owned domain;
11. renew using the same DNS-01 credentials.

Do not rely on wildcard assumptions unless a deployment explicitly
chooses that path.

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

## Health Checks

Use the same checks before and after deploys.

Primary stack:

```bash
./ops/db_mirror_restore.sh cluster-status
```

Mirror stack:

```bash
./ops/db_mirror_restore.sh mirror-status
```

When Docker is available, validate both Compose files before rollout:

```bash
docker compose -f compose.yaml config
docker compose -f compose.mirror.yaml config
```

The health check is clear when the Galera probe reports `wsrep_ready`
`ON` and `wsrep_cluster_status` `Primary`, and the Compose config render
completes without errors.

## Production Preflight

Run this checklist before a real rollout:

1. confirm `ops/opsconfig.yaml` and the local secret files exist;
2. render the runtime exports with `python3 ops/opsconfig.py primary`;
3. run `bash -n` over the repo-owned shell scripts;
4. run the Compose config render commands above where Docker is
   available;
5. verify `./ops/db_mirror_restore.sh cluster-status` and
   `./ops/db_mirror_restore.sh mirror-status`;
6. run `./ops/deploy.sh`;
7. run `./ops/backup.sh backup`.

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

## Installation rehearsal

A fresh install must work from `ops/opsconfig.yaml` plus local secrets.

The proof installation, mirror hosts, and storefront host must all be
able to use the same contract whether they run on one host or on
separate hosts.

The same config profile feeds the repo-owned rehearsal path:

1. render the shell exports with `python3 ops/opsconfig.py primary`;
2. run `./ops/deploy.sh`;
3. run `./ops/backup.sh backup`;
4. run `./ops/deploy_mirror.sh`;
5. verify `./ops/db_mirror_restore.sh mirror-status`.
