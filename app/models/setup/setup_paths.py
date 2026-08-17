"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_paths.py
Descrição : Representa os caminhos utilizados na geração do Setup.
--------------------------------------------------------------------
"""

from pathlib import Path


class SetupPaths:
    """
    Representa os caminhos físicos utilizados pelo Setup.
    """

    def __init__(
        self,
        publish_path: Path,
        setup_output_path: Path,
        output_msi: Path,
        aip_path: Path,
        visualstudio_setup_path: Path | None = None,
    ) -> None:

        self.publish_path = (
            publish_path
        )

        self.setup_output_path = (
            setup_output_path
        )

        self.output_msi = (
            output_msi
        )

        self.aip_path = (
            aip_path
        )
        self.visualstudio_setup_path = (
            visualstudio_setup_path
        )