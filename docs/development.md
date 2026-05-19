# Development
**Doc ID:** DEVELOPMENT
**Doc Type:** operator-guide
**Project Version:** 0.4.0
**DevCovenant Version:** 1.0.1b5

## Overview

APRP development happens from a clean checkout plus the tracked config
shape. The goal is to keep the framework installable, testable, and
generalized before any specific client deployment is layered on top.

Run development commands from the APRP checkout root.

The local loop should exercise the same contract as the runtime:
DocTypes, service helpers, config rendering, and repo-owned operator
scripts.

## Local loop

1. edit the Python modules, docs, or operator scripts that own the
   behavior;
2. keep `ops/opsconfig.yaml.example` and `ops/opsconfig.yaml` aligned in
   shape;
3. run `python3 -m unittest discover -v`;
4. run `devcovenant gate --verify`;
5. run `devcovenant run`;
6. run `devcovenant gate --close`;
7. run `devcovenant check`.

## Runtime checks

- use `python3 ops/opsconfig.py primary` to inspect the exported runtime
  shape;
- use `python3 ops/opsconfig.py mirror` to inspect the mirror shape;
- use `bash -n` on repo-owned shell scripts before rollout;
- use `docker compose -f compose.yaml config` and
  `docker compose -f compose.mirror.yaml config` when Docker is
  available.

## Development rules

- do not hardcode hosts in compose or shell helpers;
- keep secrets out of tracked files;
- keep showcase data separate from production records;
- keep the test suite aligned with new DocTypes and service helpers.
