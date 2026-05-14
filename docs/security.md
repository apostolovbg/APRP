# Security and Public Demo
**Doc ID:** SECURITY
**Doc Type:** operator-guide
**Project Version:** 0.4.0
**DevCovenant Version:** 1.0.1b5

## Overview

APRP treats security as part of the product, not a later add-on. Public
entrypoints must be HTTPS-only, secrets must stay out of tracked files,
and public users must never receive unrestricted ERP access.

The controlled showcase mode is the public demo surface. Its rules live
in `docs/showcase.md`, and its seed/reset helpers live in
`aprp.aprp.showcase_services`.

## Public entrypoints

- enforce HTTPS and redirect plain HTTP;
- use secure cookies for any public session state;
- keep HSTS enabled for public surfaces;
- keep admin surfaces separate from public storefront surfaces;
- do not expose ERP administration to anonymous users.

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
