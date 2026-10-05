# ---- pre-check 1: create ConfigMap
x(){ echo; echo "\$ $*"; bash -c "$*" 2>&1; echo "[rc=$?]"; }
cd /workspace/t; mkdir -p cm; cd cm
printf 'SHOP_NAME=ร้านน้องส้ม\nSHOP_THEME=sunset\n# comment\nEMPTY=\n' > shop.env
printf 'วันนี้ปลาทูสด\n' > announcement.txt
printf 'server { listen 8080; }\n' > default.conf
x kubectl version
x kubectl create configmap demo --from-literal=SHOP_NAME=ร้านน้องส้ม --from-literal=APP_THEME=sunset
x kubectl get cm demo -o yaml
x kubectl describe cm demo
x kubectl create configmap files --from-file=announcement.txt --from-file=nginx.conf=default.conf
x kubectl get cm files -o jsonpath="{.data}"
x kubectl create configmap envf --from-env-file=shop.env
x kubectl get cm envf -o jsonpath="{.data}"
x kubectl create configmap dir --from-file=. --dry-run=client -o yaml
x kubectl create configmap demo2 --from-literal=a=1 --dry-run=client -o yaml
head -c 16 /dev/urandom > logo.bin
x kubectl create configmap bin --from-file=logo.bin
x "kubectl get cm bin -o yaml | grep -A1 binaryData"
head -c 1100000 /dev/zero | tr '\0' a > big.txt
x kubectl create configmap big --from-file=big.txt
head -c 1048000 /dev/zero | tr '\0' a > big2.txt
x kubectl create configmap big2 --from-file=big2.txt
x kubectl create configmap demo --from-literal=x=1
x kubectl get cm -n kube-system
x "kubectl get cm -n kube-system coredns -o jsonpath='{.data.Corefile}'"
x "kubectl get cm -n kube-system kube-proxy -o yaml | head -30"
x kubectl get cm -A
x "kubectl get cm kube-root-ca.crt -o yaml | head -8"
x kubectl api-resources --api-group= -o wide | grep -i configmap
x kubectl explain pod.spec.containers.env.valueFrom.configMapKeyRef
x kubectl explain configmap.immutable
