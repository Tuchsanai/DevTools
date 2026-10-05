R="../r.sh lab01"
$R . 'kubectl api-resources | grep -E "^NAME|^secrets"'
$R . 'kubectl get secret -A'
$R . 'kubectl create secret generic demo --from-literal=username=som --from-literal=password=meow1234'
$R . 'kubectl get secret demo'
$R . 'kubectl get secret demo -o yaml'
$R . "kubectl get secret demo -o jsonpath='{.data.password}'; echo"
$R . "kubectl get secret demo -o jsonpath='{.data.password}' | base64 -d; echo"
$R . 'echo bWVvdzEyMzQ= | base64 -d; echo'
$R . 'echo meow1234 | base64'
$R . 'echo -n meow1234 | base64'
$R . 'echo bWVvdzEyMzQK | base64 -d | od -c | head -2'
$R . 'kubectl describe secret demo'
$R . "kubectl get secret demo -o go-template='{{range \$k,\$v := .data}}{{\$k}}={{\$v | base64decode}}{{\"\\n\"}}{{end}}'"
$R . 'kubectl create secret generic demo --from-literal=password=again'
$R . 'kubectl create secret generic demo2 --from-literal=password=meow1234 --dry-run=client -o yaml'
