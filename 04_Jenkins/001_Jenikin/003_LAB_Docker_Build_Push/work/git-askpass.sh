#!/bin/sh
# Askpass helper: reads credentials from environment variables only.
case "$1" in
  Username*) printf '%s\n' "${GITHUB_USER:-x-access-token}" ;;
  *) printf '%s\n' "$GITHUB_TOKEN" ;;
esac
