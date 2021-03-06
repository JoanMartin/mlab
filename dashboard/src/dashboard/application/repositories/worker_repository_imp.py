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

import datetime
import json
from typing import List

from dashboard.application.conf.config import PROJECT
from dashboard.application.datasource.zk_datasource_imp import ZKDatasourceImp
from dashboard.domain.entities.worker import Worker
from dashboard.domain.repositories.model_repository import ModelRepository
from dashboard.domain.repositories.worker_repository import WorkerRepository


class WorkerRepositoryImp(WorkerRepository):
    workers_path = "/%s/workers" % PROJECT

    def __init__(self, zk_datasource: ZKDatasourceImp,
                 model_repository: ModelRepository):
        self.model_resitory = model_repository
        self.zk_datasource = zk_datasource
        self.worker_down_callbacks = []

        # @self.zk_datasource.zk.ChildrenWatch(self.workers_path)
        # def watch_children(children):
        #     print("Children are now: %s" % children)
        #     for callback in self.worker_down_callbacks:
        #         callback(children)

    def subscribe_worker_down_callback(self, callback):
        self.worker_down_callbacks.append(callback)

    def get_available_workers(self) -> List[Worker]:
        workers = []
        if self.zk_datasource.zk.exists(self.workers_path) is not None:
            workers_info = self.zk_datasource.zk.get_children(self.workers_path)
            for worker_info in workers_info:
                znode_worker = self.zk_datasource.zk.get(
                    "%s/%s" % (self.workers_path, worker_info))
                worker_data = json.loads(znode_worker[0].decode('utf-8'))
                ts = datetime.datetime.fromtimestamp(znode_worker[1].created)
                is_up = False
                if self.zk_datasource.zk.exists(
                        "%s/%s/up" % (self.workers_path, worker_info)):
                    is_up = True
                    znode_up = self.zk_datasource.zk.get(
                        "%s/%s/up" % (self.workers_path, worker_info))
                    ts = datetime.datetime.fromtimestamp(znode_up[1].created)

                worker = Worker(host_name=worker_info,
                                host=worker_data["host"],
                                number_of_instances=worker_data["instances"],
                                model=self.model_resitory.get_model_by_id(
                                    self._get_model_for_worker(worker_info)),
                                group=self._get_group_for_worker(worker_info),
                                ts=ts,
                                up=is_up,
                                model_loaded=any(
                                    state in worker_data.keys() for state in
                                    ["model_error", "model_success"]),
                                model_error="model_error" in worker_data.keys(),
                                auto_model_publisher=worker_data.get(
                                    "auto_model_publisher", 'false') == 'true')
                workers.append(worker)
        return workers

    def get_groups(self):
        return list(set(
            [worker.group for worker in self.get_available_workers() if
             worker.group is not None]))

    def get_workers_host_by_group(self, group: str) -> List[str]:
        workers_info = self.zk_datasource.zk.get_children(self.workers_path)
        return [worker_info for worker_info in workers_info if
                self._get_group_for_worker(worker_info) == group]

    def set_group_in_worker(self, worker_host: str, group: str):
        self.zk_datasource.update_or_create(
            "%s/%s" % (self.workers_path, worker_host), "group",
            group)

    def set_model_in_worker(self, worker_host: str, model_id: str):
        self.zk_datasource.update_or_create(
            "%s/%s" % (self.workers_path, worker_host), "model",
            model_id)

    def _get_group_for_worker(self, worker_host):
        group_path = "%s/%s/group" % (self.workers_path, worker_host)
        if self.zk_datasource.zk.exists(group_path) is not None:
            return self.zk_datasource.zk.get(group_path)[0].decode('utf-8')

    def _get_model_for_worker(self, worker_host):
        model_path = "%s/%s/model" % (self.workers_path, worker_host)
        if self.zk_datasource.zk.exists(model_path) is not None:
            return self.zk_datasource.zk.get(model_path)[0].decode('utf-8')

    def set_auto_model_publisher(self, worker_host: str, enable: bool):
        worker_data = self.zk_datasource.zk.get(
            "%s/%s" % (self.workers_path, worker_host))
        data = json.loads(worker_data[0].decode("utf-8"))
        data["auto_model_publisher"] = enable
        self.zk_datasource.zk.set("%s/%s" % (self.workers_path, worker_host),
                                  json.dumps(data).encode('utf-8'))

    def is_enable_auto_model_publication(self, worker_host):
        return any(worker.auto_model_publisher for worker in
                   self.get_available_workers())

    def remove_worker(self, worker_host: str):
        worker_path = "%s/%s" % (self.workers_path, worker_host)
        if self.zk_datasource.zk.exists(worker_path) is not None:
            self.zk_datasource.zk.delete(worker_path)

