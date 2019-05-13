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


import base64
import io
import json

import requests
from collections import namedtuple
from PIL import Image
import numpy as np

Context = namedtuple('Context',
                     'model_name, model_version, method, rest_uri, grpc_uri, '
                     'custom_attributes, request_content_type, accept_header')


# def handler(data, context):
# encoded_image = base64.b64encode(data.read()).decode('utf-8')
# tfs_input_data = json.dumps({"instances": [{"b64": encoded_image}]})
# response = requests.post(context.rest_uri, data=tfs_input_data)
# return response.body, context.accept_header


def input_handler(data, context):
    """ Pre-process request input before it is sent to TensorFlow Serving REST API

    Args:
        data (obj): the request data, in format of dict or string
        context (Context): an object containing request and configuration details

    Returns:
        (dict): a JSON-serializable dict that contains request body and headers
    """

    if context.request_content_type == 'application/x-image':
        # image_as_bytes = io.BytesIO(data.read())
        # image = Image.open(image_as_bytes)
        # instance = np.expand_dims(image, axis=0)
        # return '{ "b64": {} }'.format(base64.b64encode(data.read()))

        #encoded_image = base64.b64encode(data.read()).decode('utf-8')
        #instance = [{"b64": encoded_image}]
        #print(instance)
        #data = json.dumps({"instances": instance})
        #print(data)
        # return json.dumps({"examples":[{"image":{"b64": encoded_image}}]})
        # return json.dumps({"instances": [{"b64": encoded_image}]})

        #image_as_bytes = io.BytesIO(data.read())
        #image = Image.open(image_as_bytes)
        #instance = np.expand_dims(image, axis=0)
        #return json.dumps({"instances": instance.tolist()})

        encoded_image = base64.b64encode(data.read()).decode('utf-8')
        instance = [{"b64": encoded_image}]
        return json.dumps({"instances": instance})

    else:
        _return_error(415, 'Unsupported content type "{}"'.format(context.request_content_type or 'Unknown'))


def output_handler(data, context):
    """Post-process TensorFlow Serving output before it is returned to the client.

    Args:
        data (obj): the TensorFlow serving response
        context (Context): an object containing request and configuration details

    Returns:
        (bytes, string): data to return to client, response content type
    """
    if data.status_code != 200:
        raise Exception(data.content.decode('utf-8'))
    response_content_type = context.accept_header
    prediction = data.content
    return prediction, response_content_type


def _return_error(code, message):
    raise ValueError('Error: {}, {}'.format(str(code), message))
