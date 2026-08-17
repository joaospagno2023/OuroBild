"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_file_parser.py
Descrição : Extrai arquivos do projeto de Setup Visual Studio.
--------------------------------------------------------------------
"""

import re

from pathlib import Path

from app.models.setup.setup_file import (
    SetupFile,
)


class SetupFileParser:
    """
    Extrai os arquivos existentes em um projeto .vdproj.
    """

    def parse(
        self,
        content: str,
        publish_path: Path,
    ) -> list[SetupFile]:
        """
        Extrai os arquivos do conteúdo do .vdproj.
        """

        if content is None:
            raise ValueError(
                "Conteúdo do Setup não foi informado."
            )

        if publish_path is None:
            raise ValueError(
                "PublishPath não foi informado."
            )

        publish_path = Path(
            publish_path,
        )

        results: list[SetupFile] = []

        pattern = re.compile(
            r'"AssemblyAsmDisplayName"\s*=\s*"8:(.*?)"\s*'
            r'"ScatterAssemblies"\s*'
            r'\{.*?'
            r'"Name"\s*=\s*"8:(.*?)"\s*'
            r'"Attributes"\s*=\s*"3:\d+"\s*'
            r'\}.*?'
            r'"SourcePath"\s*=\s*"8:(.*?)"\s*'
            r'"TargetName"',
            re.DOTALL,
        )

        for match in pattern.finditer(
            content,
        ):
            assembly_display_name = (
                match.group(1)
            )

            name = (
                match.group(2)
            )

            source_path = (
                match.group(3)
            )

            results.append(
                SetupFile(
                    name=name,
                    source_path=source_path,
                    publish_path=(
                        publish_path / name
                    ),
                    assembly_display_name=(
                        assembly_display_name
                    ),
                )
            )

        return results