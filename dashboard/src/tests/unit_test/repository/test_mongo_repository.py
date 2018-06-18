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


from unittest import TestCase

from dashboard.application.repositories.mongo_repository import \
    get_concat_mongo_uri


class TestMongoRepository(TestCase):

    def test_get_concat_mongo_uri_receive_only_beginning_part(self):
        mongo_uri = "mongodb://localhost:27017"
        database_name = "test_database"
        self.assertEqual(get_concat_mongo_uri(database_name, mongo_uri),
                         "mongodb://localhost:27017/test_database")

    def test_get_concat_mongo_uri_receive_only_beginning_part2(self):
        mongo_uri = "mongodb://localhost:27017/"
        database_name = "test_database"
        self.assertEqual(get_concat_mongo_uri(database_name, mongo_uri),
                         "mongodb://localhost:27017/test_database")

    def test_get_concat_mongo_uri_receive_full_uri(self):
        mongo_uri = "mongodb://localhost:27017/?readPreference=primary"
        database_name = "test_database"
        self.assertEqual(get_concat_mongo_uri(database_name, mongo_uri),
                         "mongodb://localhost:27017/test_database?readPreference=primary")
