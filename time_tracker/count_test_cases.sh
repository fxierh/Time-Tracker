#!/usr/bin/env bash

# shellcheck disable=SC2038
test_case_count=$(find "$1"/'classic_tracker' "$1"/'templates' "$1"/'static' "$1"/'time_tracker' \
-name 'test*.py' \
| xargs cat | grep -c "def test")

echo "$test_case_count"
