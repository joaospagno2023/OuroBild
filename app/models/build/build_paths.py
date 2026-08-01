"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_paths.py
Descrição : Caminhos utilizados durante a execução de um Build.
--------------------------------------------------------------------
"""

from pathlib import Path


class BuildPaths:
    """
    Representa todos os caminhos utilizados
    durante a execução de um Build.
    """

    def __init__(
        self,
    ) -> None:

        #
        # Ambiente
        #

        self.workspace_root: Path | None = None

        #
        # Código fonte
        #

        self.source_root: Path | None = None

        self.project_file: Path | None = None

        #
        # Publicação
        #

        self.publish_root: Path | None = None

        #
        # Installer
        #

        self.installer_file: Path | None = None

        #
        # Artefatos
        #

        self.artifacts_root: Path | None = None

        #
        # Logs
        #

        self.logs_root: Path | None = None