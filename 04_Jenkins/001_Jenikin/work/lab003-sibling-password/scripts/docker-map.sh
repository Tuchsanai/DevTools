# Sourced by lab.sh before running a README host block verbatim. Owner: yolo3 (LAB003 sibling/password run).
# Defines docker() that maps the learner names/ports in the README text onto this run's isolated resources:
#   devtools → $DC   jenkins → $JC   cicd-net → $NET   jenkins_home → $VOL
#   2222:22 / 8080:8080 / 3000:3000 → 127.0.0.1:$P_SSH / $P_JENKINS / $P_APP
# `docker run --name devtools|jenkins` also gets --network-alias devtools|jenkins, so the name inside cicd-net
# is exactly what the Jenkinsfile uses. Any argument still naming a learner resource after mapping is refused.
: "${DC:?}" "${JC:?}" "${NET:?}" "${VOL:?}" "${P_SSH:?}" "${P_JENKINS:?}" "${P_APP:?}"
docker() {
  case "${1:-}" in run|rm|network|exec|cp|ps|start|logs|inspect|port) ;; *) echo "docker-map: refused subcommand '${1:-}'" >&2; return 97 ;; esac
  local a out=() alias_for=""
  for a in "$@"; do
    case "$a" in
      devtools) a=$DC; alias_for=devtools ;;
      jenkins) a=$JC; alias_for=jenkins ;;
      devtools:*) a=$DC:${a#devtools:} ;;
      jenkins:*) a=$JC:${a#jenkins:} ;;
      cicd-net) a=$NET ;;
      jenkins_home:*) a=$VOL:${a#jenkins_home:} ;;
      'name=^devtools$') a="name=^$DC\$" ;;
      'name=^jenkins$') a="name=^$JC\$" ;;
      2222:22) a=127.0.0.1:$P_SSH:22 ;;
      8080:8080) a=127.0.0.1:$P_JENKINS:8080 ;;
      3000:3000) a=127.0.0.1:$P_APP:3000 ;;
    esac
    out+=("$a")
  done
  for a in "${out[@]}"; do
    case "$a" in
      devtools|jenkins|cicd-net|jenkins_home|devtools:*|jenkins:*|jenkins_home:*|*'^devtools$'*|*'^jenkins$'*)
        echo "docker-map: refused learner resource '$a'" >&2; return 98 ;;
    esac
  done
  if [ "${out[0]}" = run ] && [ -n "$alias_for" ]; then
    out=(run --network-alias "$alias_for" "${out[@]:1}")
  fi
  command docker "${out[@]}"
}
