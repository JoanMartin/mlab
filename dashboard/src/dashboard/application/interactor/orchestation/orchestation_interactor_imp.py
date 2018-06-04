import datetime
from typing import Dict
import pytz
import tzlocal

import timeago

from dashboard.domain.entities.worker import Worker
from dashboard.domain.interactor.orchestation.orchestation_interator import \
    OrchestationInteractor
from dashboard.domain.repositories.worker_repository import WorkerRepository


class OrchestationInteractorImp(OrchestationInteractor):
    def __init__(self, worker_repository: WorkerRepository):
        self.worker_repository = worker_repository

    def load_model_on_group(self, group: str, model_id: str):
        workers_host = self.worker_repository.get_workers_host_by_group(group)
        for worker_host in workers_host:
            self.worker_repository.set_model_in_worker(worker_host, model_id)

    def set_group_to_worker(self, host_id: str, group_name: str):
        self.worker_repository.set_group_in_worker(host_id, group_name)

    def _get_workers_grouped(self):

        def _map_worker_to_dict(worker: Worker) -> Dict:
            return {
                "name": worker.host_name,
                "swagger_uri": "http://%s:9090" % worker.host,
                "worker": worker.number_of_instances,
                "ts": timeago.format(worker.ts, datetime.datetime.utcnow()),
                "model_name": "Model not loaded" if worker.model is None else worker.model.name + " - " + str(
                    worker.model.ts),
                "group": worker.group,
                "running": worker.up,
                "auto_model_publisher": worker.auto_model_publisher
            }

        workers = self.worker_repository.get_available_workers()

        return [_map_worker_to_dict(worker) for worker in workers]

    def get_group_workers(self):
        groups = {}
        without_group = []
        clusters = self._get_workers_grouped()
        for cluster in clusters:
            if cluster["group"] is None:
                without_group.append(cluster)
            elif cluster["group"] in groups.keys():
                groups[cluster["group"]].append(cluster)
            else:
                groups[cluster["group"]] = [cluster]
        return groups, without_group

    def load_model_on_host(self, host, model_id):
        self.worker_repository.set_model_in_worker(worker_host=host,
                                                   model_id=model_id)

    def set_auto_model_publisher(self, host: str, enable: bool):
        self.worker_repository.set_auto_model_publisher(worker_host=host,
                                                        enable=enable)

    def get_groups(self):
        return self.worker_repository.get_groups()
