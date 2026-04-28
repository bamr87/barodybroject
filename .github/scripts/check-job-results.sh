#!/usr/bin/env bash
set -euo pipefail

if (( $# == 0 )); then
  echo "No job results were provided."
  exit 1
fi

failed=0

for job_result in "$@"; do
  job_name=${job_result%%=*}
  result=${job_result#*=}

  echo "$job_name: $result"

  case "$result" in
    success|skipped)
      ;;
    *)
      failed=1
      ;;
  esac
done

if (( failed )); then
  echo "One or more required workflow jobs failed."
  exit 1
fi

echo "Required workflow jobs completed successfully."