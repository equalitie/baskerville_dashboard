# Copyright (c) 2020, eQualit.ie inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
import os
import uuid
import traceback

from pathlib import Path
from baskerville_dash.auth import login_required
from baskerville_dash.utils.helpers import ResponseEnvelope, get_qparams, \
    get_rss, response_jsonified, get_active_app, get_extension, is_compressed, \
    get_ip_list, unzip, get_user_by_org_uuid
from flask import Blueprint, request, session, url_for
from werkzeug.utils import secure_filename
from baskerville.db.models import RequestSet, Runtime
from baskerville_dash.db.manager import SessionManager


results_app = Blueprint('results_app', __name__)

ALLOWED_FILES = {'csv', 'zip', 'xlsx', }


@results_app.route('/results/upload', methods=['POST'])
@login_required
def upload_file():
    response = ResponseEnvelope()
    code = 200
    rs_start = None
    try:
        # check if the post request has the file part
        if 'file' not in request.files:
            response.message = 'No file part'
            return response_jsonified(response, code)
        file = request.files['file']
        if file.filename == '':
            response.message = 'No selected file'
            return response_jsonified(response, code)
        if file and get_extension(file.filename) in ALLOWED_FILES:
            from baskerville_dash.app import app
            client_uuid = session['org_uuid']
            file_uuid = str(uuid.uuid4())
            filename = f'{file_uuid}_{secure_filename(file.filename)}'
            folder = os.path.join(app.config['UPLOAD_FOLDER'], client_uuid)
            full_path = os.path.join(folder, filename)
            Path(folder).mkdir(parents=True, exist_ok=True)
            file.save(full_path)
            if is_compressed(full_path):
                ext = get_extension(full_path)
                dot_ext = f'.{ext}'
                _ext = f'_{ext}'
                unzip(full_path, full_path.replace(dot_ext, _ext))
                filename = filename.replace(dot_ext, _ext)
                print('filename: ', filename)

            response.message = f'Csv uploaded successfully.'
            response.data = {
                'org_uuid': client_uuid,
                'filename': filename,
                'results': url_for(
                    'results_app.get_results',
                    app_id=file_uuid,
                )
            }
        else:
            raise ValueError('Invalid extension')
    except Exception as e:
        traceback.print_exc()
        response.message = str(e)
        code = 500
    return response_jsonified(response, code)


@results_app.route('/results', methods=['POST'])
@login_required
def get_all_results():
    _q_filter = get_qparams(request)
    re = ResponseEnvelope()
    sm = SessionManager()
    re.success = True
    re.data = []
    re.message = f'No results found.'
    code = 200
    ip_list = None
    try:
        org_uuid = session['org_uuid']
        ip_file_name = request.args.get('file')
        print('FILE: ip_file_name', ip_file_name)
        user = get_user_by_org_uuid(org_uuid)
        if not user:
            code = 404
            re.success = False
            re.message = 'No user found'
            print(re.message)
            return response_jsonified(re, code)
        if ip_file_name:
            print('in ip_file_name')
            ip_list = get_ip_list(ip_file_name, org_uuid)
            print('in ip_list', ip_list)
        re.data = get_rss(**_q_filter, user=user, ip_list=ip_list)
        re.message = f'The request sets for {">>"}'
    except Exception as e:
        sm.session.rollback()
        re.success = False
        re.message = str(e)
        code = 500
        traceback.print_exc()

    return response_jsonified(re, code)


@results_app.route('/results/<app_id>', methods=['POST'])
@login_required
def get_results(app_id):
    from flask import session
    _q_filter = get_qparams(request)
    re = ResponseEnvelope()
    re.success = True
    re.data = []
    re.message = f'No results found.'
    code = 200
    ip_list = None
    try:
        sm = SessionManager()
        org_uuid = session['org_uuid']
        ip_file_name = request.args.get('file')
        user = get_user_by_org_uuid(org_uuid)
        if not user:
            code = 404
            re.success = False
            re.message = 'No user found'
            print(re.message)
            return response_jsonified(re, code)
        runtime_q = sm.session.query(Runtime)
        app_data = get_active_app(app_id)
        if not app_data:
            runtime = runtime_q.filter(
                Runtime.file_name.like(f'%{app_id}%')
            ).first()
        else:
            runtime = runtime_q.filter_by(
                file_name=app_data['file_path']
            ).first()
        if runtime:
            if ip_file_name:
                ip_list = get_ip_list(ip_file_name, org_uuid)
            re.data = get_rss(
                **_q_filter, id_runtime=runtime.id, user=user, ip_list=ip_list
            )
            re.message = f'The results of {app_id} run.'
        else:
            re.data = {'data': [], 'total_num_pages': 0}
            re.message = 'No results'
    except Exception as e:
        re.success = False
        re.message = str(e)
        code = 500
        traceback.print_exc()

    print('>>>>>>>>>>>>>> ', response_jsonified(re, code))
    return response_jsonified(re, code)