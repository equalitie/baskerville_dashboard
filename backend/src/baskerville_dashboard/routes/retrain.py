# Copyright (c) 2020, eQualit.ie inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
import json
import traceback

from baskerville.models.config import TrainingConfig
from baskerville.util.helpers import parse_config
from baskerville_dashboard.auth import login_required
from baskerville_dashboard.utils.helpers import ResponseEnvelope, \
    submit_training
from baskerville_dashboard.utils.helpers import response_jsonified
from baskerville_dashboard.vm.retrain_vm import RetrainVm
from flask import Blueprint, request, session

retrain_app = Blueprint('retrain_app', __name__)


@retrain_app.route('/retrain', methods=('POST',))
@login_required
def retrain():
    response = ResponseEnvelope()
    try:
        code = 200
        data = request.get_json()
        config = parse_config(data=data['config'])
        training_config = TrainingConfig(config).validate()
        if len(training_config.errors) > 0:
            response.success = False
            response.message = f'The following errors were found in ' \
                               f'the configuration:' \
                               f'{training_config.serialized_errors}'
            response.data = data
            code = 403
        else:
            submit_training(RetrainVm(data['config'], session['org_uuid']))
            response.success = True
            response.message = 'Re-train submitted. ' \
                               'You will be notified for the outcome.'
            response.data = data
    except Exception as e:
        code = 500
        traceback.print_exc()
        response.success = False
        response.message = str(e)

    return response_jsonified(response, code)
