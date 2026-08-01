"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : production_build_environment_builder.py
Descrição : Responsável por preparar um BuildContext para Produção.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.abstractions.build_environment_builder import (
    BuildEnvironmentBuilder,
)
from app.models.build.build_context import BuildContext


class ProductionBuildEnvironmentBuilder(
    BuildEnvironmentBuilder,
):
    """
    Prepara o contexto para Produção.
    """

    def build(
        self,
        context: BuildContext,
    ) -> None:

        if context.environment is None:
            raise ValueError("Environment não informado.")

        if context.project is None:
            raise ValueError("Projeto não informado.")

        workspace = context.environment.root_path

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