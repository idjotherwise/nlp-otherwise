#!/bin/sh
set -e
cd $(dirname "$0")/..
cd _notebooks/

ERRORS=""

for file in *.ipynb
do
    if papermill --kernel python3 "${file}" "${file}" && git add "${file}"; then
        echo "Successfully refreshed and added ${file}\n\n\n\n"
    else
        echo "Error Refreshing ${file}"
        ERRORS="${ERRORS}, ${file}"
    fi
donenb

# Emit Errors if Exists so Downstream Task can open an issue
if [ -z "$ERRORS" ]
then
    echo "::set-output name=error_bool::false"
else
    echo "These files failed to update properly: ${ERRORS}"
    echo "::set-output name=error_bool::true"
    echo "::set-output name=error_str::${ERRORS}"
fi