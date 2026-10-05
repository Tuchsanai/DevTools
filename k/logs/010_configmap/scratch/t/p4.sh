x(){ echo; echo "\$ $*"; bash -c "$*" 2>&1; echo "[rc=$?]"; }
cd /workspace/t
x "kubectl exec optpod -- ls /etc/opt-cm"
x kubectl get pod volpod envpod
# update timing test (3 rounds)
for r in 1 2 3; do
  v="ปลาทูรอบ$r"
  kubectl patch cm shop-config --type merge -p "{\"data\":{\"announcement.txt\":\"$v\n\",\"SHOP_NAME\":\"ร้านใหม่$r\"}}" >/dev/null
  t0=$(date +%s)
  while :; do
    out=$(kubectl exec volpod -- cat /etc/all/announcement.txt)
    [ "$out" = "$v" ] && break
    [ $(( $(date +%s) - t0 )) -gt 150 ] && { echo timeout; break; }
    sleep 1
  done
  echo "round $r: volume updated after $(( $(date +%s) - t0 ))s"
  echo "  subPath file: $(kubectl exec volpod -- cat /etc/som/announcement.txt)"
  echo "  /etc/all/SHOP_NAME: $(kubectl exec volpod -- cat /etc/all/SHOP_NAME)"
  echo "  env in envpod: $(kubectl exec envpod -- printenv SHOP_NAME)"
  sleep 5
done
x "kubectl exec volpod -- ls -la /etc/all | head -6"
x "kubectl exec volpod -- ls -laR /etc/some | grep today"
