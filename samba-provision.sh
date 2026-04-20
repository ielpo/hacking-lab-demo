#!/bin/bash

set -euo pipefail

PRIVATE_DIR="/var/lib/samba/private"
SAM_DB="${PRIVATE_DIR}/sam.ldb"
USERS_FILE="/opt/lab/demo_users.csv"

provision_domain() {
  rm -f /etc/samba/smb.conf

  samba-tool domain provision \
    --server-role=dc \
    --use-rfc2307 \
    --dns-backend=SAMBA_INTERNAL \
    --realm="${SAMBA_REALM}" \
    --domain="${SAMBA_DOMAIN}" \
    --adminpass="${SAMBA_ADMIN_PASSWORD}"

  cp "${PRIVATE_DIR}/krb5.conf" /etc/krb5.conf

  samba-tool domain passwordsettings set \
    --complexity=off \
    --min-pwd-length=4 \
    --history-length=0 \
    --min-pwd-age=0 \
    --max-pwd-age=0

  tail -n +2 "${USERS_FILE}" | while IFS=, read -r username password; do
    samba-tool user create "${username}" "${password}"
  done
}

mkdir -p "${PRIVATE_DIR}"

if [ ! -f "${SAM_DB}" ]; then
  provision_domain
fi

exec samba --foreground --no-process-group