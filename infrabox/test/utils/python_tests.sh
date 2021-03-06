#!/bin/sh

cd /tests
coverage run --source=.,$1 --branch test.py

rc=$?

set -e

coverage report -m
coverage xml

cp results.xml /infrabox/upload/testresult
cp coverage.xml /infrabox/upload/coverage

exit $rc
