# syntax=docker/dockerfile:1.7
ARG ERPNEXT_IMAGE=frappe/erpnext:v16.36.0
FROM ${ERPNEXT_IMAGE}
USER root
COPY --chown=frappe:frappe apps/business_suite /home/frappe/frappe-bench/apps/business_suite
USER frappe
WORKDIR /home/frappe/frappe-bench
RUN bench pip install -e apps/business_suite
