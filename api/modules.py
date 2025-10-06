import os

from injector import Module, provider, singleton

from paths import ROOT_PATH
from api.shared.configs import Configs


class AppModule(Module):
    def __init__(self, build: str = "dev"):
        self.build = os.environ.get("BUILD", build)

    @provider
    @singleton
    def provide_configs(self) -> Configs:
        if self.build != "test":
            dotenv_file = ROOT_PATH / ".env"
        else:
            dotenv_file = ROOT_PATH / ".env.test"

        return Configs(
            _env_file=dotenv_file,
            _env_file_encoding="utf-8",
        )


def create_modules():
    return [
        AppModule(),
    ]
