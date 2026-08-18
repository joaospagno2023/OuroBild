"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_file_change_applier.py
Descrição : Aplica alterações de arquivos em projetos .vdproj.
--------------------------------------------------------------------
"""

from app.models.setup.setup_file_action import (
    SetupFileAction,
)

from app.models.setup.setup_file_sync import (
    SetupFileSync,
)

from app.services.setup.vdproj_component_identity_generator import (
    VdprojComponentIdentityGenerator,
)

from app.services.setup.vdproj_file_block_builder import (
    VdprojFileBlockBuilder,
)

from app.services.setup.vdproj_file_block_inserter import (
    VdprojFileBlockInserter,
)

from app.services.setup.vdproj_file_modifier import (
    VdprojFileModifier,
)

from app.services.setup.vdproj_file_template_provider import (
    VdprojFileTemplateProvider,
)


class SetupFileChangeApplier:
    """
    Aplica as alterações calculadas para os arquivos
    do Setup.
    """

    def __init__(
        self,
        modifier: VdprojFileModifier,
        template_provider: VdprojFileTemplateProvider,
        identity_generator: (
            VdprojComponentIdentityGenerator
        ),
        block_builder: VdprojFileBlockBuilder,
        block_inserter: VdprojFileBlockInserter,
    ) -> None:
        """
        Inicializa o serviço.
        """

        if modifier is None:
            raise ValueError(
                "VdprojFileModifier não foi informado."
            )

        if template_provider is None:
            raise ValueError(
                "VdprojFileTemplateProvider "
                "não foi informado."
            )

        if identity_generator is None:
            raise ValueError(
                "VdprojComponentIdentityGenerator "
                "não foi informado."
            )

        if block_builder is None:
            raise ValueError(
                "VdprojFileBlockBuilder "
                "não foi informado."
            )

        if block_inserter is None:
            raise ValueError(
                "VdprojFileBlockInserter "
                "não foi informado."
            )

        self.__modifier = modifier
        self.__template_provider = (
            template_provider
        )
        self.__identity_generator = (
            identity_generator
        )
        self.__block_builder = (
            block_builder
        )
        self.__block_inserter = (
            block_inserter
        )

    def apply(
        self,
        content: str,
        changes: list[SetupFileSync],
        template_file_name: str,
    ) -> str:
        """
        Aplica todas as alterações no conteúdo do .vdproj.

        O conteúdo recebido é tratado como uma cópia de trabalho.
        O arquivo físico original não é alterado.
        """

        if content is None:
            raise ValueError(
                "Conteúdo do .vdproj não foi informado."
            )

        if changes is None:
            raise ValueError(
                "Alterações não foram informadas."
            )

        if not template_file_name:
            raise ValueError(
                "Arquivo template não foi informado."
            )

        result = content

        for change in changes:

            if change is None:
                raise ValueError(
                    "Alteração de arquivo inválida."
                )

            if (
                change.action
                == SetupFileAction.UPDATE
            ):
                result = (
                    self.__modifier.update(
                        content=result,
                        setup_file=change,
                    )
                )

                continue

            if (
                change.action
                == SetupFileAction.REMOVE
            ):
                result = (
                    self.__modifier.remove(
                        content=result,
                        setup_file=change,
                    )
                )

                continue

            if (
                change.action
                == SetupFileAction.ADD
            ):
                result = self.__add(
                    content=result,
                    change=change,
                    template_file_name=(
                        template_file_name
                    ),
                )

                continue

            raise ValueError(
                "Ação de arquivo não suportada: "
                f"{change.action}"
            )

        return result

    def __add(
        self,
        content: str,
        change: SetupFileSync,
        template_file_name: str,
    ) -> str:
        """
        Adiciona um novo arquivo ao .vdproj.
        """

        template = (
            self.__template_provider.get_template(
                content=content,
                file_name=template_file_name,
            )
        )

        identity = (
            self.__identity_generator.generate()
        )

        block = (
            self.__block_builder.build(
                template=template.content,
                file_name=change.name,
                source_path=change.source_path,
                identity=identity,
                assembly_display_name=(
                    change.assembly_display_name
                ),
            )
        )

        return self.__block_inserter.insert(
            content=content,
            file_block=block,
        )