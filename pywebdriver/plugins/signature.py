# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2015 Akretion (http://www.akretion.com).
#   @author Sylvain Calador <sylvain.calador@akretion.com>
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import logging
import os

from flask_cors import cross_origin
from flask import request, make_response, jsonify
import pymtp

from pywebdriver import app, config, drivers


SIGNATURE_FILENAME='signature.svg'
DOWNLOAD_PATH='/tmp'

@app.route('/hw_proxy/get_signature', methods=['GET'])
@cross_origin()
def get_signautre_http():

    file_ = None
    data = None

    try:
        mtp = pymtp.MTP()
        mtp.connect()
    except Exception, err:
        app.logger.error('Device not connected %s' % str(err))
        return jsonify(jsonrpc='2.0', result=data)

    for f in mtp.get_filelisting():
        if f.filename == SIGNATURE_FILENAME:
            file_ = f
            break
    if file_:
        dest_file = os.path.join(DOWNLOAD_PATH, SIGNATURE_FILENAME)
        try:
            mtp.get_file_to_file(file_.item_id, dest_file)
            app.logger.debug('file downloaded to %s' % dest_file)
            data = open(dest_file, 'r').read()
            app.logger.debug(data)
            mtp.delete_object(file_.item_id)
        except Exception, err:
            app.logger.error('error during file transfer %s' % str(err))
    else:
        app.logger.error('file not found on the device: %s' % SIGNATURE_FILENAME)

    mtp.disconnect()
    return jsonify(jsonrpc='2.0', result=data)