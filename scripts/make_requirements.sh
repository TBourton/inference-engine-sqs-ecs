#!/bin/bash

set -x

if [[ ${1:-""} == "-fresh" ]] ; then
    rm requirements.txt
    rm test-requirements.txt
    rm lint-requirements.txt
fi

pip-compile --no-emit-index-url --extra producer --extra consumer -o requirements.txt pyproject.toml
pip-compile --extra testing --no-emit-index-url --pip-args='-c=requirements.txt' -o test-requirements.txt pyproject.toml
pip-compile --extra linting --no-emit-index-url --pip-args='-c=requirements.txt -c=test-requirements' -o lint-requirements.txt pyproject.toml
