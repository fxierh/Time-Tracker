#!/usr/bin/env bash

# shellcheck disable=SC2038
frontend_line_count=$(find "$1"/'classic_tracker' "$1"/'templates' "$1"/'static' "$1"/'time_tracker' \
\( -name '*.html' -o -name '*.css' -o -name '*.js' -o -name '*.txt' \) \
| xargs wc -l | tail -n 1 | awk '{print $1}')

backend_line_count=$(find "$1"/'classic_tracker' "$1"/'templates' "$1"/'static' "$1"/'time_tracker' \
\( -name '*.py' -a -not -name 'test*.py' -o -name '*.sh' \) \
| xargs wc -l | tail -n 1 | awk '{print $1}')

test_line_count=$(find "$1"/'classic_tracker' "$1"/'templates' "$1"/'static' "$1"/'time_tracker' \
\( -name 'test*.py' \) \
| xargs wc -l | tail -n 1 | awk '{print $1}')

echo "$frontend_line_count"

echo "$backend_line_count"

echo "$test_line_count"
