# coding: utf-8
from application.controllers.base_model_controller import BaseModelController


class BenchmarkModelController(BaseModelController):
    def on_get(self, req, resp):
        model_request = {}
        resp.media = {"model_response": ''}
