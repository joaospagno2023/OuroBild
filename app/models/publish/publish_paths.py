"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_paths.py
Descrição : Caminhos utilizados durante a execução do Publish.
--------------------------------------------------------------------
"""

from pathlib import Path


class PublishPaths:
    """
    Armazena os caminhos utilizados durante a execução
    do Publish.
    """

    def __init__(
        self,
    ) -> None:

        #
        # Projeto
        #

        self.project_file: Path | None = None

        self.project_directory: Path | None = None

        #
        # Publicação
        #

        self.output_directory: Path | None = None

        self.publish_profile: Path | None = None