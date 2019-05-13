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
import shutil
import subprocess
import sys
import time

import pytest

import requests


PING_URL = 'http://localhost:8080/ping'
INVOCATIONS_URL = 'http://localhost:8080/invocations'


@pytest.fixture(scope='module', autouse=True, params=['1'])
def volume(tmpdir_factory, request):
    try:
        model_dir = os.path.join(tmpdir_factory.mktemp('test'), 'model')
        code_dir = os.path.join(model_dir, 'code')
        test_example = 'test/resources/examples/test{}'.format(request.param)

        model_src_dir = 'test/resources/models'
        shutil.copytree(model_src_dir, model_dir)
        shutil.copytree(test_example, code_dir)

        volume_name = f'model_volume_{request.param}'
        subprocess.check_call(
            'docker volume create --name {} --opt type=none '
            '--opt device={} --opt o=bind'.format(volume_name, model_dir).split())
        yield volume_name
    finally:
        subprocess.check_call(f'docker volume rm {volume_name}'.split())


@pytest.fixture(scope='module', autouse=True, params=['1.12'])
def container(request, volume):
    try:
        command = (
            'docker run --name sagemaker-tensorflow-serving-test -p 8080:8080'
            ' --mount type=volume,source={},target=/opt/ml/model,readonly'
            ' -e SAGEMAKER_TFS_DEFAULT_MODEL_NAME=half_plus_three'
            ' -e SAGEMAKER_TFS_NGINX_LOGLEVEL=info'
            ' -e SAGEMAKER_BIND_TO_PORT=8080'
            ' -e SAGEMAKER_SAFE_PORT_RANGE=9000-9999'
            ' sagemaker-tensorflow-serving:{}-cpu serve'
        ).format(volume, request.param)

        proc = subprocess.Popen(command.split(), stdout=sys.stdout, stderr=subprocess.STDOUT)

        attempts = 0
        while attempts < 5:
            time.sleep(3)
            try:
                requests.get('http://localhost:8080/ping')
                break
            except:
                attempts += 1
                pass

        yield proc.pid
    finally:
        subprocess.check_call('docker rm -f sagemaker-tensorflow-serving-test'.split())


def make_headers(content_type, method):
    headers = {
        'Content-Type': content_type,
        'X-Amzn-SageMaker-Custom-Attributes': 'tfs-model-name=half_plus_three,tfs-method=%s' % method
    }
    return headers

def test_ping_service():
    response = requests.get(PING_URL)
    assert 200 == response.status_code


def test_sleep():
    import time
    time.sleep(600000)
