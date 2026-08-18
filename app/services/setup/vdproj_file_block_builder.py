"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : vdproj_file_block_builder.py
Descrição : Cria blocos de arquivos para projetos .vdproj.
--------------------------------------------------------------------
"""

import re

from app.models.setup.vdproj_component_identity import (
    VdprojComponentIdentity,
)


class VdprojFileBlockBuilder:
    """
    Cria um novo bloco de arquivo .vdproj a partir
    de um bloco existente.
    """

    def build(
        self,
        template: str,
        file_name: str,
        source_path: str,
        identity: VdprojComponentIdentity,
        assembly_display_name: str | None = None,
    ) -> str:
        """
        Cria um novo bloco utilizando o template informado.
        """

        if not template:
            raise ValueError(
                "Template do arquivo não foi informado."
            )

        if not file_name:
            raise ValueError(
                "Nome do arquivo não foi informado."
            )

        if not source_path:
            raise ValueError(
                "SourcePath não foi informado."
            )

        if identity is None:
            raise ValueError(
                "Identidade do componente não foi informada."
            )

        result = template

        #
        # Name dentro do ScatterAssemblies.
        #

        result = re.sub(
            r'("Name"\s*=\s*"8:)[^"]+(")',
            lambda match: (
                match.group(1)
                + file_name
                + match.group(2)
            ),
            result,
            count=1,
        )

        #
        # SourcePath.
        #

        result = re.sub(
            r'("SourcePath"\s*=\s*"8:)[^"]+(")',
            lambda match: (
                match.group(1)
                + source_path
                + match.group(2)
            ),
            result,
            count=1,
        )

        #
        # AssemblyAsmDisplayName.
        #

        if assembly_display_name:

            result = re.sub(
                r'("AssemblyAsmDisplayName"\s*=\s*"8:)[^"]+(")',
                lambda match: (
                    match.group(1)
                    + assembly_display_name
                    + match.group(2)
                ),
                result,
                count=1,
            )

        #
        # Identidade do componente.
        #
        # Formato real do .vdproj:
        #
        # "{GUID}:_IDENTIFIER"
        #

        result = re.sub(
            r'(?m)^(\s*)"\{'
            r'[A-Fa-f0-9-]{36}'
            r'\}:_[A-Fa-f0-9]{32}'
            r'"\s*$',
            lambda match: (
                match.group(1)
                + '"{'
                + identity.guid
                + "}:_"
                + identity.identifier
                + '"'
            ),
            result,
            count=1,
        )

        return result