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
from app.services.workspace.solution_locator_service import (
    SolutionLocatorService,
)


class ProductionBuildEnvironmentBuilder(
    BuildEnvironmentBuilder,
):
    """
    Prepara o contexto para Produção.
    """

    def __init__(
        self,
        solution_locator: SolutionLocatorService,
    ) -> None:
        """
        Inicializa o Builder.
        """

        self.__solution_locator = solution_locator

    def build(
        self,
        context: BuildContext,
    ) -> None:
        """
        Prepara os caminhos do ambiente.
        """

        if context.environment is None:
            raise ValueError(
                "Environment não informado."
            )

        if context.project is None:
            raise ValueError(
                "Projeto não informado."
            )

        workspace = context.environment.root_path

        context.paths.workspace_root = workspace

        context.paths.project_file = (
            workspace /
            Path(
                context.project.project_path,
            )
        )

        context.paths.solution_file = (
            self.__solution_locator.find_solution(
                context.paths.project_file,
            )
        )

        print("=" * 80)
        print("PRODUCTION BUILDER")
        print("PROJECT :", context.paths.project_file)
        print("SOLUTION:", context.paths.solution_file)
        print("=" * 80)

        context.paths.source_root = (
            context.paths.project_file.parent
        )

        context.paths.publish_root = (
            workspace /
            Path(
                context.project.publish_path,
            )
        )

        context.paths.installer_file = (
            workspace /
            Path(
                context.project.aip_path,
            )
        )