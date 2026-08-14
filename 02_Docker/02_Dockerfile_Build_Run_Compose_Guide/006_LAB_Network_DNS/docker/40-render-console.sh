#!/bin/sh
set -e

template=/usr/share/nginx/html/index.html.tpl
output=/usr/share/nginx/html/index.html

# ทำให้ค่าปลอดภัยสำหรับ HTML ก่อนนำไปใช้เป็น replacement ของ sed
html_escape() {
  printf '%s' "$1" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g; s/"/\&quot;/g; s/|/\&#124;/g; s/\\/\\\\/g; s/&/\\\&/g'
}

hostname_value=$(hostname)
service_value=${SERVICE_NAME:-$hostname_value}
ip_value=$(ip -4 -o addr show scope global 2>/dev/null | awk '{print $4}' | paste -sd ' ' -)
dns_value=$(awk '$1 == "nameserver" {print $2}' /etc/resolv.conf | paste -sd ' ' -)
iface_value=$(ip -o link show | awk -F': ' '{name=$2; sub(/@.*/, "", name); print name}' | paste -sd ' ' -)
served_value=$(date -u '+%Y-%m-%d %H:%M:%S UTC')

[ -n "$ip_value" ] || ip_value=none
[ -n "$dns_value" ] || dns_value=none
[ -n "$iface_value" ] || iface_value=none

service_safe=$(html_escape "$service_value")
hostname_safe=$(html_escape "$hostname_value")
ip_safe=$(html_escape "$ip_value")
dns_safe=$(html_escape "$dns_value")
iface_safe=$(html_escape "$iface_value")
served_safe=$(html_escape "$served_value")

sed \
  -e "s|__SERVICE_NAME__|$service_safe|g" \
  -e "s|__HOSTNAME__|$hostname_safe|g" \
  -e "s|__CONTAINER_IP__|$ip_safe|g" \
  -e "s|__DNS_RESOLVER__|$dns_safe|g" \
  -e "s|__NETWORK_IFACES__|$iface_safe|g" \
  -e "s|__SERVED_AT__|$served_safe|g" \
  "$template" > "$output"

printf 'Rendered Container Network Console: %s\n' "$output"
