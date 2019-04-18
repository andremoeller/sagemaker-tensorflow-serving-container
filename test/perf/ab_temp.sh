#!/usr/bin/env bash
TEMPFILE='/tmp/perftest_data.csv'


# Tall payloads (1048576 CSV lines, 699051 JSONL lines, 1 JSON line)
python test/perf/data_generator.py -c 'text/csv' -s 5 -p 10 -u MB > $TEMPFILE || exit $?
ab -k -n 25 -c 1 -p "$TEMPFILE" -T 'text/csv' -H 'X-Amzn-SageMaker-Custom-Attributes: tfs-model-name=nonexistent' http://localhost:8080/invocations

TEMPFILE='/tmp/perftest_data.json'
python test/perf/data_generator.py -c 'application/json' -s 5 -p 10 -u MB > $TEMPFILE || exit $?
ab -k -n 25 -c 1 -p "$TEMPFILE" -T 'application/json' -H 'X-Amzn-SageMaker-Custom-Attributes: tfs-model-name=nonexistent' http://localhost:8080/invocations

TEMPFILE='/tmp/perftest_data.jsonl'
python test/perf/data_generator.py -c 'application/jsonlines' -s 5 -p 10 -u MB > $TEMPFILE || exit $?
ab -k -n 25 -c 1 -p "$TEMPFILE" -T 'application/jsonlines' -H 'X-Amzn-SageMaker-Custom-Attributes: tfs-model-name=nonexistent' http://localhost:8080/invocations

python test/perf/data_generator.py -c 'text/csv' -s 5 -p 1 -u MB > $TEMPFILE || exit $?
ab -k -n 100 -c 1 -p "$TEMPFILE" -T 'text/csv' -H 'X-Amzn-SageMaker-Custom-Attributes: tfs-model-name=nonexistent' http://localhost:8080/invocations

TEMPFILE='/tmp/perftest_data.json'
python test/perf/data_generator.py -c 'application/json' -s 5 -p 1 -u MB > $TEMPFILE || exit $?
ab -k -n 100 -c 1 -p "$TEMPFILE" -T 'application/json' -H 'X-Amzn-SageMaker-Custom-Attributes: tfs-model-name=nonexistent' http://localhost:8080/invocations

TEMPFILE='/tmp/perftest_data.jsonl'
python test/perf/data_generator.py -c 'application/jsonlines' -s 5 -p 1 -u MB > $TEMPFILE || exit $?
ab -k -n 100 -c 1 -p "$TEMPFILE" -T 'application/jsonlines' -H 'X-Amzn-SageMaker-Custom-Attributes: tfs-model-name=nonexistent' http://localhost:8080/invocations
