"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : workspace_resolver.py
Descrição : Responsável por resolver as informações de um projeto
             dentro de um Workspace.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.abstractions.environment_repository import (
    EnvironmentRepository,
)

from app.abstractions.project_repository import (
    ProjectRepository,
)

from app.workspace.workspace_context import (
    WorkspaceContext,
)

from app.exceptions.project_not_found_exception import (
    ProjectNotFoundException,
)

from app.exceptions.environment_not_found_exception import (
    EnvironmentNotFoundException,
)

from app.utils.pipeline_logger import (
    PipelineLogger,
)


class WorkspaceResolver:
    """
    Responsável por resolver um projeto
    dentro de um ambiente.
    """

    def __init__(
        self,
        project_repository: ProjectRepository,
        environment_repository: EnvironmentRepository,
    ) -> None:
        """
        Inicializa o resolver.
        """

        if project_repository is None:
            raise ValueError(
                "ProjectRepository não foi informado."
            )

        if environment_repository is None:
            raise ValueError(
                "EnvironmentRepository não foi informado."
            )

        self.__project_repository = (
            project_repository
        )

        self.__environment_repository = (
            environment_repository
        )

    def resolve(
        self,
        project_id: str,
        environment_id: str,
        version: str | None = None,
        revision: str | None = None,
    ) -> WorkspaceContext:
        """
        Resolve todas as informações necessárias
        para trabalhar com um projeto.

        Args:
            project_id:
                Identificador do projeto.

            environment_id:
                Identificador do ambiente.

            version:
                Versão do build (obrigatória quando o
                ambiente utiliza resolver "versioned").

            revision:
                Revisão do build (obrigatória quando o
                ambiente utiliza resolver "versioned").

        Returns:
            WorkspaceContext contendo projeto,
            ambiente e caminho do arquivo.

        Raises:
            ProjectNotFoundException:
                Quando o projeto não existe.

            EnvironmentNotFoundException:
                Quando o ambiente não existe.

            ValueError:
                Quando o ambiente é "versioned" e
                version/revision não foram informados,
                ou a versão está em formato inválido.
        """

        #
        # ============================================================
        # Diagnóstico - parâmetros recebidos
        # ============================================================
        #

        PipelineLogger.info(
            "WORKSPACE RESOLVER DIAGNOSTICO - PARAMETROS RECEBIDOS"
        )

        PipelineLogger.info(
            f"project_id.............: {project_id!r}"
        )

        PipelineLogger.info(
            f"environment_id.........: {environment_id!r}"
        )

        PipelineLogger.info(
            f"version................: {version!r}"
        )

        PipelineLogger.info(
            f"revision...............: {revision!r}"
        )

        project = (
            self.__project_repository.get_by_id(
                project_id=project_id,
            )
        )

        if project is None:
            raise ProjectNotFoundException(
                project_id=project_id,
            )

        environment = (
            self.__environment_repository.get_by_id(
                environment_id=environment_id,
            )
        )

        if environment is None:
            raise EnvironmentNotFoundException(
                environment_id=environment_id,
            )

        #
        # ============================================================
        # Diagnóstico - ambiente resolvido
        # ============================================================
        #

        PipelineLogger.info(
            "WORKSPACE RESOLVER DIAGNOSTICO - AMBIENTE"
        )

        PipelineLogger.info(
            f"environment.resolver...: {environment.resolver!r}"
        )

        PipelineLogger.info(
            f"environment.root_path..: {environment.root_path!r}"
        )

        #
        # Para ambientes versionados, a estrutura física do
        # TFS insere a versão entre a raiz do ambiente e o
        # caminho do projeto:
        #
        #   root_path\<major.minor>\<build>\<project_path>
        #
        # Sem isso, o caminho resolvido aponta para uma pasta
        # genérica sem versão, que não corresponde ao que o
        # Build realmente gera (ver VersionedBuildEnvironmentBuilder).
        #
        if environment.resolver == "versioned":

            if not version:
                raise ValueError(
                    "Versão não informada para ambiente "
                    "versionado."
                )

            if not revision:
                raise ValueError(
                    "Revisão não informada para ambiente "
                    "versionado."
                )

            version_parts = version.strip().split(".")

            if len(version_parts) < 3:
                raise ValueError(
                    "Versão inválida para ambiente "
                    f"versionado: {version}"
                )

            version_root = ".".join(
                version_parts[:-1]
            )

            version_build = version_parts[-1]

            workspace_root = (
                Path(environment.root_path)
                / version_root
                / version_build
            )

        else:

            workspace_root = Path(
                environment.root_path,
            )

        #
        # ============================================================
        # Diagnóstico - workspace_root resolvido
        # ============================================================
        #

        PipelineLogger.info(
            f"workspace_root..........: {workspace_root}"
        )

        project_file = (
            workspace_root
            / project.project_path
        )

        PipelineLogger.info(
            f"project_file............: {project_file}"
        )

        return WorkspaceContext(
            project=project,
            environment=environment,
            project_file=project_file,
        )