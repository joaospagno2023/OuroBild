"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : versioned_build_environment_builder.py
Descrição : Responsável por preparar um BuildContext para um ambiente
             versionado.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.abstractions.build_environment_builder import (
    BuildEnvironmentBuilder,
)
from app.models.build.build_context import BuildContext
from app.services.workspace.solution_locator_service import (
    SolutionLocatorService,
)


class VersionedBuildEnvironmentBuilder(
    BuildEnvironmentBuilder,
):
    """
    Prepara o contexto para um ambiente versionado.
    """

    def __init__(
        self,
        solution_locator: SolutionLocatorService,
    ) -> None:
        self.__solution_locator = solution_locator

    def build(
        self,
        context: BuildContext,
    ) -> None:
        """
        Prepara todos os caminhos do Build.
        """

        if context.environment is None:
            raise ValueError(
                "Environment não informado."
            )

        if context.project is None:
            raise ValueError(
                "Projeto não informado."
            )

        if context.request is None:
            raise ValueError(
                "BuildRequest não informado."
            )

        print(
            "DEBUG VERSIONED BUILDER | "
            f"request={context.request!r} | "
            f"version={getattr(context.request, 'version', None)!r} | "
            f"revision={getattr(context.request, 'revision', None)!r}"
        )

        if context.request.version is None:
            raise ValueError(
                "Versão não informada."
            )

        if context.request.revision is None:
            raise ValueError(
                "Revisão não informada."
            )

        #
        # A estrutura física do TFS para ambientes versionados
        # utiliza a versão separada no formato:
        #
        #   Versoes\<major.minor>\<build>
        #
        # Exemplo:
        #
        #   10.4.7
        #   ->
        #   Versoes\10.4\7
        #
        version = context.request.version.strip()

        version_parts = version.split(".")

        if len(version_parts) < 3:
            raise ValueError(
                "Versão inválida para ambiente versionado: "
                f"{context.request.version}"
            )

        version_root = ".".join(
            version_parts[:-1]
        )

        version_build = version_parts[-1]

        workspace = (
            context.environment.root_path
            / version_root
            / version_build
        )

        context.paths.workspace_root = (
            workspace
        )

        context.paths.project_file = (
            workspace
            / Path(
                context.project.project_path,
            )
        )

        context.paths.solution_file = (
            self.__solution_locator.find_solution(
                context.paths.project_file,
            )
        )

        context.paths.source_root = (
            context.paths.project_file.parent
        )

        #
        # O publish_path configurado no projeto é relativo à
        # pasta do próprio projeto (source_root), não à raiz
        # da versão. Usar "workspace" aqui fazia o publish_root
        # apontar para uma pasta genérica que não corresponde
        # ao local esperado pela etapa de Setup.
        #
        context.paths.publish_root = (
            context.paths.source_root
            / Path(
                context.project.publish_path,
            )
        )

        context.paths.installer_file = (
            workspace
            / Path(
                context.project.aip_path,
            )
        )