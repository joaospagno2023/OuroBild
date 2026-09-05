"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : environment_service.py
Descrição : Regras de negócio para administração de ambientes.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.abstractions.environment_repository import (
    EnvironmentRepository,
)
from app.models.environment.build_environment import (
    BuildEnvironment,
)
from app.models.environment.create_environment_request import (
    CreateEnvironmentRequest,
)
from app.models.environment.update_environment_request import (
    UpdateEnvironmentRequest,
)


class EnvironmentService:
    """
    Serviço responsável pela administração dos ambientes.
    """

    def __init__(
        self,
        environment_repository: EnvironmentRepository,
    ) -> None:
        """
        Inicializa o serviço.
        """

        if environment_repository is None:
            raise ValueError(
                "EnvironmentRepository não foi informado."
            )

        self.__environment_repository = (
            environment_repository
        )

    def get_all(
        self,
    ) -> list[BuildEnvironment]:
        """
        Retorna todos os ambientes.
        """

        return self.__environment_repository.get_all()

    def get_by_id(
        self,
        environment_id: str,
    ) -> BuildEnvironment | None:
        """
        Retorna um ambiente pelo identificador.
        """

        if not environment_id or not environment_id.strip():
            raise ValueError(
                "EnvironmentId não foi informado."
            )

        return self.__environment_repository.get_by_id(
            environment_id.strip(),
        )

    def create(
        self,
        request: CreateEnvironmentRequest,
    ) -> BuildEnvironment:
        """
        Cria um novo ambiente.
        """

        if request is None:
            raise ValueError(
                "CreateEnvironmentRequest não foi informado."
            )

        environment_id = request.id.strip()
        name = request.name.strip()
        root_path = request.root_path.strip()

        self.__validate(
            environment_id=environment_id,
            name=name,
            root_path=root_path,
        )

        existing = (
            self.__environment_repository.get_by_id(
                environment_id,
            )
        )

        if existing is not None:
            raise ValueError(
                f"Ambiente '{environment_id}' já existe."
            )

        environment = BuildEnvironment(
            id=environment_id,
            name=name,
            resolver=request.resolver.value,
            root_path=Path(root_path),
        )

        return self.__environment_repository.create(
            environment,
        )

    def update(
        self,
        environment_id: str,
        request: UpdateEnvironmentRequest,
    ) -> BuildEnvironment | None:
        """
        Atualiza um ambiente existente.
        """

        if not environment_id or not environment_id.strip():
            raise ValueError(
                "EnvironmentId não foi informado."
            )

        if request is None:
            raise ValueError(
                "UpdateEnvironmentRequest não foi informado."
            )

        normalized_id = environment_id.strip()
        name = request.name.strip()
        root_path = request.root_path.strip()

        self.__validate(
            environment_id=normalized_id,
            name=name,
            root_path=root_path,
        )

        existing = (
            self.__environment_repository.get_by_id(
                normalized_id,
            )
        )

        if existing is None:
            return None

        environment = BuildEnvironment(
            id=existing.id,
            name=name,
            resolver=request.resolver.value,
            root_path=Path(root_path),
        )

        return self.__environment_repository.update(
            environment,
        )

    @staticmethod
    def __validate(
        environment_id: str,
        name: str,
        root_path: str,
    ) -> None:
        """
        Valida os dados básicos do ambiente.
        """

        if not environment_id:
            raise ValueError(
                "Id do ambiente não foi informado."
            )

        if not name:
            raise ValueError(
                "Nome do ambiente não foi informado."
            )

        if not root_path:
            raise ValueError(
                "RootPath do ambiente não foi informado."
            )