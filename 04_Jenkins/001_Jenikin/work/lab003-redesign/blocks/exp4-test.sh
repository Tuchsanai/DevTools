docker exec jenkins ssh -G devtools-gw | grep -E '^(hostname|port|user|hostkeyalias|stricthostkeychecking) '
docker exec jenkins ssh devtools-gw true; echo "exit=$?"
