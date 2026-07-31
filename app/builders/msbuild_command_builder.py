"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : msbuild_command_builder.py
Descrição : Responsável por montar o comando de execução do MSBuild.
--------------------------------------------------------------------
"""

from app.models.build.build_configuration import BuildConfiguration
from app.models.process.command import Command
from app.models.process.command_argument import CommandArgument
from app.models.project.project import Project


class MSBuildCommandBuilder:
    """
    Responsável por construir um comando do MSBuild.
    """

    def build(
        self,
        project: Project,
        configuration: BuildConfiguration,
    ) -> Command:
        """
        Constrói o comando para execução do MSBuild.
        """

        return Command(
            executable=project.tools.msbuild.path,
            working_directory=project.project_path.parent,
            arguments=[
                CommandArgument(
                    value=str(project.project_path),
                ),
                CommandArgument(
                    value="/t:Build",
                ),
                CommandArgument(
                    value=f"/p:Configuration={configuration.configuration}",
                ),
                CommandArgument(
                    value=f"/p:Platform={configuration.platform}",
                ),
            ],
        )