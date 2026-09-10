"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : sql_project_repository.py
Descrição : Repositório de projetos utilizando SQL Server.
--------------------------------------------------------------------
"""

from sqlalchemy import (
    select,
)

from app.abstractions.project_repository import (
    ProjectRepository,
)

from app.database.connection import (
    DatabaseConnection,
)

from app.database.models.project_model import (
    ProjectModel,
)

from app.models.build.compilation_engine import (
    CompilationEngine,
)

from app.models.build.compilation_target import (
    CompilationTarget,
)

from app.models.project.create_project_request import (
    CreateProjectRequest,
)

from app.models.project.project import (
    Project,
)

from app.models.project.project_type import (
    ProjectType,
)

from app.models.project.update_project_request import (
    UpdateProjectRequest,
)


class SqlProjectRepository(
    ProjectRepository,
):
    """
    Implementação do repositório de projetos para SQL Server.
    """

    def __init__(
        self,
        database_connection: DatabaseConnection,
    ) -> None:
        """
        Inicializa o repositório.
        """

        if database_connection is None:
            raise ValueError(
                "DatabaseConnection não foi informado."
            )

        self.__database_connection = (
            database_connection
        )

    def get_all(
        self,
    ) -> list[Project]:
        """
        Retorna todos os projetos ordenados pelo identificador.
        """

        with self.__database_connection.create_session() as session:
            statement = (
                select(ProjectModel)
                .order_by(
                    ProjectModel.id,
                )
            )

            project_models = (
                session.scalars(
                    statement,
                )
                .all()
            )

            return [
                self.__to_project(
                    project_model,
                )
                for project_model in project_models
            ]

    def get_by_id(
        self,
        project_id: str,
    ) -> Project | None:
        """
        Localiza um projeto pelo identificador.
        """

        if not project_id:
            raise ValueError(
                "ProjectId não foi informado."
            )

        with self.__database_connection.create_session() as session:
            statement = (
                select(ProjectModel)
                .where(
                    ProjectModel.id == project_id,
                )
            )

            project_model = (
                session.scalars(
                    statement,
                )
                .first()
            )

            if project_model is None:
                return None

            return self.__to_project(
                project_model,
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

        with self.__database_connection.create_session() as session:
            project_model = ProjectModel(
                id=request.id,
                name=request.name,
                description=request.description,
                type=request.type.value,
                solution_path=request.solution_path,
                project_path=request.project_path,
                compilation_target=(
                    request.compilation_target.value
                ),
                compilation_engine=(
                    request.compilation_engine.value
                ),
                publish_path=request.publish_path,
                publish_profile=request.publish_profile,
                aip_path=request.aip_path,
                visualstudio_setup_path=(
                    request.visualstudio_setup_path
                ),
                output_msi=request.output_msi,
                configuration=request.configuration,
                platform=request.platform,
                enabled=request.enabled,
            )

            session.add(
                project_model,
            )

            session.flush()

            project = self.__to_project(
                project_model,
            )

            session.commit()

            return project

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

        with self.__database_connection.create_session() as session:
            statement = (
                select(ProjectModel)
                .where(
                    ProjectModel.id == project_id,
                )
            )

            project_model = (
                session.scalars(
                    statement,
                )
                .first()
            )

            if project_model is None:
                raise ValueError(
                    "Projeto não encontrado."
                )

            project_model.name = request.name
            project_model.description = request.description
            project_model.type = request.type.value
            project_model.solution_path = (
                request.solution_path
            )
            project_model.project_path = (
                request.project_path
            )
            project_model.compilation_target = (
                request.compilation_target.value
            )
            project_model.compilation_engine = (
                request.compilation_engine.value
            )
            project_model.publish_path = (
                request.publish_path
            )
            project_model.publish_profile = (
                request.publish_profile
            )
            project_model.aip_path = (
                request.aip_path
            )
            project_model.visualstudio_setup_path = (
                request.visualstudio_setup_path
            )
            project_model.output_msi = (
                request.output_msi
            )
            project_model.configuration = (
                request.configuration
            )
            project_model.platform = (
                request.platform
            )
            project_model.enabled = (
                request.enabled
            )

            session.flush()

            project = self.__to_project(
                project_model,
            )

            session.commit()

            return project

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

        with self.__database_connection.create_session() as session:
            statement = (
                select(ProjectModel)
                .where(
                    ProjectModel.id == project_id,
                )
            )

            project_model = (
                session.scalars(
                    statement,
                )
                .first()
            )

            if project_model is None:
                raise ValueError(
                    "Projeto não encontrado."
                )

            project_model.enabled = enabled

            session.flush()

            project = self.__to_project(
                project_model,
            )

            session.commit()

            return project

    @staticmethod
    def __to_project(
        project_model: ProjectModel,
    ) -> Project:
        """
        Converte o modelo SQLAlchemy para o modelo de domínio.
        """

        return Project(
            id=project_model.id,
            name=project_model.name,
            description=project_model.description,
            type=ProjectType(
                project_model.type,
            ),
            solution_path=project_model.solution_path,
            project_path=project_model.project_path,
            compilation_target=CompilationTarget(
                project_model.compilation_target,
            ),
            compilation_engine=CompilationEngine(
                project_model.compilation_engine,
            ),
            publish_path=project_model.publish_path,
            publish_profile=project_model.publish_profile,
            aip_path=project_model.aip_path,
            visualstudio_setup_path=(
                project_model.visualstudio_setup_path
            ),
            output_msi=project_model.output_msi,
            configuration=project_model.configuration,
            platform=project_model.platform,
            enabled=project_model.enabled,
        )