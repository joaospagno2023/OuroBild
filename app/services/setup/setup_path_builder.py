"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_path_builder.py
Descrição : Calcula caminhos relativos utilizados pelo Setup.
--------------------------------------------------------------------
"""

from pathlib import Path


class SetupPathBuilder:
    """
    Calcula caminhos que devem ser utilizados pelo .vdproj
    a partir do publish_path.
    """

    def build_source_path(
        self,
        vdproj_path: Path,
        publish_path: Path,
        file_name: str,
    ) -> str:
        """
        Calcula o SourcePath relativo ao diretório do .vdproj.
        """

        if vdproj_path is None:
            raise ValueError(
                "Caminho do .vdproj não foi informado."
            )

        if publish_path is None:
            raise ValueError(
                "PublishPath não foi informado."
            )

        if not file_name:
            raise ValueError(
                "Nome do arquivo não foi informado."
            )

        vdproj_directory = Path(
            vdproj_path,
        ).parent.resolve()

        publish_directory = Path(
            publish_path,
        ).resolve()

        file_path = (
            publish_directory
            / file_name
        ).resolve()

        relative_path = (
            Path(
                __import__("os").path.relpath(
                    file_path,
                    vdproj_directory,
                )
            )
        )

        return str(
            relative_path
        ).replace(
            "/",
            "\\",
        )