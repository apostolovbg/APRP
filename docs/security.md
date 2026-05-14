# Security and Public Demo
**Doc ID:** SECURITY
**Doc Type:** operator-guide
**Project Version:** 0.4.0
**DevCovenant Version:** 1.0.1b5

## Overview

APRP treats security as part of the product, not a later add-on. Public
entrypoints must be HTTPS-only, secrets must stay out of tracked files,
and public users must never receive unrestricted ERP access.

The public routing contract is role-driven, not hardcoded. The same
certificate and routing model must work for the ERP host, mirror hosts
(cluster members), the storefront host, and any other operator-owned
domain.

The controlled showcase mode is the public demo surface. Its rules live
in `docs/showcase.md`, and its seed/reset helpers live in
`aprp.aprp.showcase_services`.

## Public entrypoints

- enforce HTTPS and redirect plain HTTP;
- use secure cookies for any public session state;
- keep HSTS enabled for public surfaces;
- keep admin surfaces separate from public storefront surfaces;
- do not expose ERP administration to anonymous users.
- issue public certificates with DNS-01 ACME per hostname using
  certbot and manual TXT records;
- keep DNS provider tokens in untracked secret files;
- do not depend on wildcard issuance unless the deployment explicitly
  chooses that path.

## Secrets and state

- keep production host secrets out of git;
- keep local machine secrets in untracked env files;
- keep demo-only records separate from production rows;
- keep disposable session state resettable;
- keep backup and restore paths documented and rehearsed.

## Public demo rules

1. show the seeded storefront or showcase surface;
2. keep the disposable session scoped to the demo;
3. do not mix showcase rows with production rows;
4. reset the showcase state after the session;
5. verify the ERP boundary stayed hidden.

## DNS-01 issuance

Use DNS-01 ACME for every public hostname that APRP publishes.

The procedure is:

1. choose the hostname to publish for the ERP host, a mirror host in
   the cluster, the storefront host, or a user-owned domain;
2. verify that the DNS zone is under operator control;
3. configure `certbot` and the DNS provider credentials in an
   untracked secret file;
4. request the certificate;
5. create the `_acme-challenge` TXT record manually or let the DNS API
   create it;
6. wait for propagation and validation;
7. install the resulting certificate and key into the reverse proxy;
8. reload the proxy;
9. repeat for each hostname that needs TLS;
10. renew with the same DNS-01 credentials.
