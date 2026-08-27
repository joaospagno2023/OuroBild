"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_file_change_applier.py
Descrição : Aplica alterações de arquivos em projetos VDPROJ.
--------------------------------------------------------------------
"""

from app.models.setup.setup_file_action import (
    SetupFileAction,
)

from app.models.setup.setup_file_sync import (
    SetupFileSync,
)


class SetupFileChangeApplier:
    """
    Coordena a aplicação das alterações em um arquivo VDPROJ.

    Responsabilidades:

        UPDATE
            Atualizar bloco existente.

        REMOVE
            Remover bloco existente.

        ADD
            Criar e inserir novo bloco utilizando um template.

        KEEP
            Não realizar alteração.
    """

    def __init__(
        self,
        modifier,
        template_provider,
        identity_generator,
        block_builder,
        block_inserter,
    ):
        """
        Inicializa o serviço com suas dependências.
        """

        if modifier is None:

            raise ValueError(
                "Modifier não foi informado."
            )

        if template_provider is None:

            raise ValueError(
                "TemplateProvider não foi informado."
            )

        if identity_generator is None:

            raise ValueError(
                "IdentityGenerator não foi informado."
            )

        if block_builder is None:

            raise ValueError(
                "BlockBuilder não foi informado."
            )

        if block_inserter is None:

            raise ValueError(
                "BlockInserter não foi informado."
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
        template_file_name: str | None,
    ) -> str:
        """
        Aplica as alterações ao conteúdo VDPROJ.

        :param content:
            Conteúdo do arquivo .vdproj.

        :param changes:
            Alterações a aplicar.

        :param template_file_name:
            Nome do arquivo utilizado como template
            para operações ADD.
        """

        if content is None:

            raise ValueError(
                "Conteúdo do .vdproj não foi informado."
            )

        if changes is None:

            raise ValueError(
                "Alterações não foram informadas."
            )

        if (
            template_file_name is None
            or not str(
                template_file_name,
            ).strip()
        ):

            raise ValueError(
                "Arquivo template não foi informado."
            )

        current_content = content

        for change in changes:

            if change is None:

                continue

            action = (
                change.action
            )

            if action == SetupFileAction.KEEP:

                continue

            if action == SetupFileAction.UPDATE:

                current_content = (
                    self.__apply_update(
                        content=current_content,
                        change=change,
                    )
                )

                continue

            if action == SetupFileAction.REMOVE:

                current_content = (
                    self.__apply_remove(
                        content=current_content,
                        change=change,
                    )
                )

                continue

            if action == SetupFileAction.ADD:

                current_content = (
                    self.__apply_add(
                        content=current_content,
                        change=change,
                        template_file_name=(
                            template_file_name
                        ),
                    )
                )

                continue

            raise ValueError(
                "Ação de arquivo não suportada: "
                f"{action}"
            )

        return current_content

    def __apply_update(
        self,
        content: str,
        change: SetupFileSync,
    ) -> str:
        """
        Atualiza um bloco existente.
        """

        return (
            self.__modifier.update(
                content=content,
                setup_file=change,
            )
        )

    def __apply_remove(
        self,
        content: str,
        change: SetupFileSync,
    ) -> str:
        """
        Remove um bloco existente.
        """

        return (
            self.__modifier.remove(
                content=content,
                setup_file=change,
            )
        )

    def __apply_add(
        self,
        content: str,
        change: SetupFileSync,
        template_file_name: str,
    ) -> str:
        """
        Adiciona um novo bloco utilizando um arquivo existente
        como template.
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
                source_path=str(
                    change.source_path,
                ),
                identity=identity,
                assembly_display_name=(
                    change.assembly_display_name
                ),
            )
        )

        return (
            self.__block_inserter.insert(
                content=content,
                file_block=block,
            )
        )