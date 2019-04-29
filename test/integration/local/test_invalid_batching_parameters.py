# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import os
import subprocess


import pytest


@pytest.fixture(scope='session', autouse=True)
def volume():
    try:
        model_dir = os.path.abspath('test/resources/models')
        subprocess.check_call(
            'docker volume create --name batching_model_volume --opt type=none '
            '--opt device={} --opt o=bind'.format(model_dir).split())
        yield model_dir
    finally:
        subprocess.check_call('docker volume rm batching_model_volume'.split())


@pytest.mark.parametrize("version", ['1.11', '1.12'])
def test_run_tfs_with_invalid_batching_parameters(version):

    try:
        command = (
            'docker run --name sagemaker-tensorflow-serving-test -p 8080:8080'
            ' --mount type=volume,source=model_volume,target=/opt/ml/model,readonly'
            ' -e SAGEMAKER_TFS_ENABLE_BATCHING=1'
            ' -e SAGEMAKER_TFS_DEFAULT_MODEL_NAME=half_plus_three'
            ' -e SAGEMAKER_TFS_NGINX_LOGLEVEL=info'
            ' -e SAGEMAKER_BIND_TO_PORT=8080'
            ' -e SAGEMAKER_SAFE_PORT_RANGE=9000-9999'
            ' sagemaker-tensorflow-serving:{}-cpu serve'
        ).format(version)
        subprocess.check_output(command.split(), stderr=subprocess.STDOUT)
        assert False
    except subprocess.CalledProcessError as e:
        output = str(e.output)
        assert 'SAGEMAKER_TFS_BATCHING_MAX_ENQUEUED_BATCHES' in output and \
             'SAGEMAKER_TFS_BATCHING_TIMEOUT_MICROS' in output and \
             'SAGEMAKER_TFS_BATCHING_MAX_BATCH_SIZE' in output
    finally:
        subprocess.check_call('docker rm -f sagemaker-tensorflow-serving-test'.split())