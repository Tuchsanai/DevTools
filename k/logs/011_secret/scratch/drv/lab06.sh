R="../r.sh lab06"; D=labs/lab06-projected
$R $D 'kubectl apply -f proj.yaml && kubectl wait --for=condition=Ready pod/proj --timeout=120s'
$R $D 'kubectl exec proj -- ls -laLR /etc/som'
$R $D 'kubectl exec proj -- sh -c "cat /etc/som/pod-name; echo; cat /etc/som/db/password; echo; cat /etc/som/announcement.txt"'
$R $D 'kubectl exec proj -- mount | grep /etc/som'
$R $D 'kubectl exec proj -- ls -la /var/run/secrets/kubernetes.io/serviceaccount/'
$R $D 'kubectl apply -f builder-token.yaml; sleep 3; kubectl get secret builder-token'
$R $D 'kubectl describe secret builder-token'
$R $D 'kubectl get sa builder -o yaml'
$R $D 'kubectl create token builder --duration=10m | cut -c1-40; echo ...'
$R $D "kubectl create token builder --duration=10m | cut -d. -f2 | base64 -d 2>/dev/null | head -c 400; echo"
$R $D 'kubectl get secret'
