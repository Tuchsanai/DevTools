kubectl -n som-shop get pod som-test-health 2>&1 | tail -1
helm test som -n som-shop >/dev/null; kubectl -n som-shop get pod som-test-health 2>&1 | tail -1
sleep 5; kubectl -n som-shop get pod som-test-health 2>&1 | tail -1
helm test som -n som-shop --logs >/dev/null; sleep 5; kubectl -n som-shop get pod som-test-health 2>&1 | tail -1
