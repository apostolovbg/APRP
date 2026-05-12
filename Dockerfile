# Shared APRP runtime image for the backend, websocket, queue, and scheduler.
#
# The repo mounts its code at runtime. This image adds the backup toolchain and
# keeps the bench environment ready for DevCovenant and operator commands.

ARG ERPNEXT_TAG=v16.1.0
FROM frappe/erpnext:${ERPNEXT_TAG}

USER root

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
      --no-install-recommends \
      ca-certificates \
      git \
      rclone \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /backups/aprp \
    && chown -R frappe:frappe /backups

USER frappe

RUN /home/frappe/frappe-bench/env/bin/python -m pip install --no-cache-dir \
      virtualenv==20.34.0 \
      cfgv==3.5.0 \
      identify==2.6.19 \
      nodeenv==1.10.0 \
      distlib==0.4.0 \
      platformdirs==4.9.6 \
      python-discovery==1.2.2 \
      pre-commit==4.5.1 \
      pytest==9.0.3

COPY devcovenant/runtime-requirements.lock /tmp/devcovenant-runtime.lock
RUN /home/frappe/frappe-bench/env/bin/python -m pip install --no-cache-dir \
      -r /tmp/devcovenant-runtime.lock

WORKDIR /home/frappe/frappe-bench/apps/aprp
