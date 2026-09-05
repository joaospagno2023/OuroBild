"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_service.py
Descrição : Executa operações relacionadas aos projetos.
--------------------------------------------------------------------
"""

from app.abstractions.project_repository import ProjectRepository
from app.models.project.create_project_request import CreateProjectRequest
from app.models.project.project import Project
from app.models.project.update_project_request import UpdateProjectRequest


class ProjectService:
    """
    Responsável pelas operações administrativas dos projetos.
    """

    def __init__(
        self,
        project_repository: ProjectRepository,
    ) -> None:
        """
        Inicializa o serviço.
        """

        if project_repository is None:
            raise ValueError(
                "ProjectRepository não foi informado."
            )

        self.__project_repository = project_repository

    def get_all(self) -> list[Project]:
        """
        Retorna todos os projetos.
        """

        return self.__project_repository.get_all()

    def get_by_id(
        self,
        project_id: str,
    ) -> Project | None:
        """
        Retorna um projeto pelo identificador.
        """

        return self.__project_repository.get_by_id(
            project_id,
        )

    def create(
        self,
        request: CreateProjectRequest,
    ) -> Project:
        """
        Cria um novo projeto.
        """

        if request is None:
            raise ValueError(
                "CreateProjectRequest não foi informado."
            )

        project_id = request.id.strip()
        name = request.name.strip()
        description = request.description.strip()

        if not project_id:
            raise ValueError(
                "ProjectId não foi informado."
            )

        if not name:
            raise ValueError(
                "Nome do projeto não foi informado."
            )

        if not description:
            raise ValueError(
                "Descrição do projeto não foi informada."
            )

        existing_project = (
            self.__project_repository.get_by_id(
                project_id,
            )
        )

        if existing_project is not None:
            raise ValueError(
                "ProjectId já está cadastrado."
            )

        normalized_request = CreateProjectRequest(
            id=project_id,
            name=name,
            description=description,
            type=request.type,
            solution_path=(
                request.solution_path.strip()
                if request.solution_path
                else None
            ),
            project_path=(
                request.project_path.strip()
                if request.project_path
                else None
            ),
            compilation_target=request.compilation_target,
            compilation_engine=request.compilation_engine,
            publish_path=request.publish_path.strip(),
            publish_profile=(
                request.publish_profile.strip()
                if request.publish_profile
                else None
            ),
            aip_path=request.aip_path.strip(),
            visualstudio_setup_path=(
                request.visualstudio_setup_path.strip()
                if request.visualstudio_setup_path
                else None
            ),
            output_msi=request.output_msi.strip(),
            network_path=request.network_path.strip(),
            configuration=request.configuration.strip(),
            platform=request.platform.strip(),
            enabled=request.enabled,
        )

        return self.__project_repository.create(
            request=normalized_request,
        )

    def update(
        self,
        project_id: str,
        request: UpdateProjectRequest,
    ) -> Project:
        """
        Atualiza um projeto existente.
        """

        if not project_id:
            raise ValueError(
                "ProjectId não foi informado."
            )

        if request is None:
            raise ValueError(
                "UpdateProjectRequest não foi informado."
            )

        name = request.name.strip()
        description = request.description.strip()

        if not name:
            raise ValueError(
                "Nome do projeto não foi informado."
            )

        if not description:
            raise ValueError(
                "Descrição do projeto não foi informada."
            )

        existing_project = (
            self.__project_repository.get_by_id(
                project_id,
            )
        )

        if existing_project is None:
            raise ValueError(
                "Projeto não encontrado."
            )

        normalized_request = UpdateProjectRequest(
            name=name,
            description=description,
            type=request.type,
            solution_path=(
                request.solution_path.strip()
                if request.solution_path
                else None
            ),
            project_path=(
                request.project_path.strip()
                if request.project_path
                else None
            ),
            compilation_target=request.compilation_target,
            compilation_engine=request.compilation_engine,
            publish_path=request.publish_path.strip(),
            publish_profile=(
                request.publish_profile.strip()
                if request.publish_profile
                else None
            ),
            aip_path=request.aip_path.strip(),
            visualstudio_setup_path=(
                request.visualstudio_setup_path.strip()
                if request.visualstudio_setup_path
                else None
            ),
            output_msi=request.output_msi.strip(),
            network_path=request.network_path.strip(),
            configuration=request.configuration.strip(),
            platform=request.platform.strip(),
            enabled=request.enabled,
        )

        return self.__project_repository.update(
            project_id=project_id,
            request=normalized_request,
        )

    def update_status(
        self,
        project_id: str,
        enabled: bool,
    ) -> Project:
        """
        Atualiza somente o status do projeto.
        """

        if not project_id:
            raise ValueError(
                "ProjectId não foi informado."
            )

        return self.__project_repository.update_status(
            project_id=project_id,
            enabled=enabled,
        )