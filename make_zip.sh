#!/usr/bin/env bash

set -e

if ! command -v virtualenv &> /dev/null; then
    echo "virtualenv could not be found, please install using 'pip3 install virtualenv'"
    exit 1
fi

ENV_NAME="hockey_draft_env"
ZIP_NAME="hockey_draft.zip"

echo "Installing pre-reqs"

python3 -m venv $ENV_NAME
source $ENV_NAME/bin/activate
pip3 install -r requirements.txt
deactivate

rm -f $ZIP_NAME 2> /dev/null

echo "Creating $ZIP_NAME, adding site-packages"
pushd $ENV_NAME/lib/python3.*/site-packages
zip --quiet -r ../../../../$ZIP_NAME .
popd

echo "Adding python files to $ZIP_NAME"
zip --quiet -r $ZIP_NAME *.py app/ 2024/ css/

echo "Success"
