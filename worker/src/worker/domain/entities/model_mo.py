# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Bluekiri V5 BigData Team <bigdata@bluekiri.com>.
#
# This program is free software: you can redistribute it and/or  modify
# it under the terms of the GNU Affero General Public License, version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# As a special exception, the copyright holders give permission to link the
# code of portions of this program with the OpenSSL library under certain
# conditions as described in each individual source file and distribute
# linked combinations including the program with the OpenSSL library. You
# must comply with the GNU Affero General Public License in all respects for
# all of the code used other than as permitted herein. If you modify file(s)
# with this exception, you may extend this exception to your version of the
# file(s), but you are not obligated to do so. If you do not wish to do so,
# delete this exception statement from your version. If you delete this
# exception statement from all source files in the program, then also delete
# it in the license file.

import logging

import dill as pkl
from mongoengine import *

from worker.application.conf.config import MONGO_CONNECTION_URI, MONGO_DATABASE

connect(host=MONGO_CONNECTION_URI, db=MONGO_DATABASE, connect=False)
logger = logging.getLogger()


class Model(Document):
    meta = {"collection": "mlmodel", "strict": False}
    name = StringField(required=True)
    deserialized_model_instance = None
    pickle = FileField(required=True)

    def get_model_instance(self):
        pkl.dill._reverse_typemap['ClassType'] = type
        if self.deserialized_model_instance is None:
            content = self.pickle.read()
            self.deserialized_model_instance = pkl.loads(content)
        return self.deserialized_model_instance
