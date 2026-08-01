"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : json_environment_repository.py
Descrição : Repositório responsável pela leitura dos ambientes.
--------------------------------------------------------------------
"""

import json
from pathlib import Path

from app.abstractions.environment_repository import (
    EnvironmentRepository,
)
from app.models.environment.build_environment import (
    BuildEnvironment,
)


class JsonEnvironmentRepository(
    EnvironmentRepository,
):
    """
    Implementação baseada em JSON.
    """

    def __init__(
        self,
        configuration_path: Path,
    ) -> None:

        self.__file = (
            configuration_path / "environments.json"
        )

    def get_all(
        self,
    ) -> list[BuildEnvironment]:

        with self.__file.open(
            mode="r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        return [
            BuildEnvironment.model_validate(item)
            for item in data
        ]

    def get_by_id(
        self,
        environment_id: str,
    ) -> BuildEnvironment | None:

        for environment in self.get_all():

            if environment.id == environment_id:
                return environment

        return None