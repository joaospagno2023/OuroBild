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


class VersionedBuildEnvironmentBuilder(
    BuildEnvironmentBuilder,
):
    """
    Prepara o contexto para um ambiente versionado.
    """

    def build(
        self,
        context: BuildContext,
    ) -> None:
        """
        Prepara todos os caminhos do Build.
        """

        if context.environment is None:
            raise ValueError("Environment não informado.")

        if context.project is None:
            raise ValueError("Projeto não informado.")

        if context.request is None:
            raise ValueError("BuildRequest não informado.")

        if context.request.version is None:
            raise ValueError("Versão não informada.")

        if context.request.revision is None:
            raise ValueError("Revisão não informada.")

        workspace = (
            context.environment.root_path
            / context.request.version
            / str(context.request.revision)
        )

        context.paths.workspace_root = workspace

        context.paths.project_file = (
            workspace /
            Path(context.project.project_path)
        )

        context.paths.source_root = (
            context.paths.project_file.parent
        )

        context.paths.publish_root = (
            workspace /
            Path(context.project.publish_path)
        )

        context.paths.installer_file = (
            workspace /
            Path(context.project.aip_path)
        )