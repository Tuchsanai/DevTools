#!/bin/sh
set -eu

assert_equal() {
  expected=$1
  actual=$2
  label=$3

  if [ "$actual" != "$expected" ]; then
    echo "FAIL: $label" >&2
    echo "  expected: $expected" >&2
    echo "  actual:   $actual" >&2
    exit 1
  fi

  echo "PASS: $label -> $actual"
}

docker build -q -t lab4-cmd:1.0 ./cmd-only >/dev/null
docker build -q -t lab4-entrypoint:1.0 ./entrypoint-only >/dev/null
docker build -q -t lab4-both:1.0 ./both >/dev/null

assert_equal "CMD default" "$(docker run --rm lab4-cmd:1.0)" "CMD default"
assert_equal "CMD override" "$(docker run --rm lab4-cmd:1.0 /bin/echo 'CMD override')" "CMD override"
assert_equal "" "$(docker run --rm lab4-entrypoint:1.0)" "ENTRYPOINT without arguments"
assert_equal "hello Docker" "$(docker run --rm lab4-entrypoint:1.0 hello Docker)" "ENTRYPOINT appends arguments"
assert_equal "ENTRYPOINT: CMD default" "$(docker run --rm lab4-both:1.0)" "ENTRYPOINT plus CMD default"
assert_equal "ENTRYPOINT: custom" "$(docker run --rm lab4-both:1.0 custom)" "CLI replaces CMD only"
assert_equal "entrypoint replaced" "$(docker run --rm --entrypoint /bin/sh lab4-both:1.0 -c 'echo entrypoint replaced')" "--entrypoint override"

cmd_config=$(docker image inspect lab4-cmd:1.0 --format 'Entrypoint={{json .Config.Entrypoint}} Cmd={{json .Config.Cmd}}')
entrypoint_config=$(docker image inspect lab4-entrypoint:1.0 --format 'Entrypoint={{json .Config.Entrypoint}} Cmd={{json .Config.Cmd}}')
both_config=$(docker image inspect lab4-both:1.0 --format 'Entrypoint={{json .Config.Entrypoint}} Cmd={{json .Config.Cmd}}')

echo "$cmd_config"
echo "$entrypoint_config"
echo "$both_config"
echo "ALL LAB 4 CHECKS PASSED"
