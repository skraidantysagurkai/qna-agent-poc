from api.modules import AppModule

from api.app import create_app
from starlette.testclient import TestClient


def prepare_api_server():
    def step(context):
        app = create_app(create_test_modules())
        context.app = app
        context.client = TestClient(app)
        context.injector = app.state.injector

    return step


def create_test_modules():
    return [AppModule("test")]
