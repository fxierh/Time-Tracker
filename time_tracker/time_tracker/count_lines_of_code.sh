#!/usr/bin/env bash

# shellcheck disable=SC2038
frontend_line_count=$(find "$1"/'classic_tracker' "$1"/'templates' "$1"/'static' "$1"/'time_tracker' \
-type f \
\( -name '*.html' -o -name '*.css' -o -name '*.js' -o -name '*.txt' \) \
-not -path "$1"/'static/third_party/*' \
| xargs wc -l | tail -n 1 | awk '{print $1}')

backend_line_count=$(find "$1"/'classic_tracker' "$1"/'templates' "$1"/'static' "$1"/'time_tracker' \
-type f \
\( -name '*.py' -a -not -name 'test*.py' -o -name '*.sh' \) \
-not -path "$1"/'static/third_party/*' \
| xargs wc -l | tail -n 1 | awk '{print $1}')

test_line_count=$(find "$1"/'classic_tracker' "$1"/'templates' "$1"/'static' "$1"/'time_tracker' \
-type f \
\( -name 'test*.py' \) \
-not -path "$1"/'static/third_party/*' \
| xargs wc -l | tail -n 1 | awk '{print $1}')

test_case_count=$(find "$1"/'classic_tracker' "$1"/'templates' "$1"/'static' "$1"/'time_tracker' \
-type f \
-name 'test*.py' \
-not -path "$1"/'static/third_party/*' \
| xargs cat | grep -c "def test")

echo "$frontend_line_count"

echo "$backend_line_count"

echo "$test_line_count"

echo "$test_case_count"
