"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : cleanup_rules_provider.py
Descrição : Fornece as regras de limpeza do Build.
--------------------------------------------------------------------
"""

from app.models.cleanup.cleanup_rule import (
    CleanupAction,
    CleanupRule,
    CleanupTarget,
)


class CleanupRulesProvider:
    """
    Fornece as regras padrão de limpeza do OuroBuild.

    As regras globais são aplicadas a todos os projetos.

    As regras específicas são aplicadas somente quando
    o project_id correspondente estiver sendo processado.

    Regras específicas de projeto possuem prioridade sobre
    as regras globais.
    """

    @staticmethod
    def get_rules(
        project_id: str | None = None,
    ) -> list[CleanupRule]:
        """
        Retorna as regras aplicáveis ao projeto.
        """

        rules = (
            CleanupRulesProvider.__get_global_rules()
        )

        if project_id is not None:

            rules.extend(
                CleanupRulesProvider.__get_project_rules(
                    project_id=project_id,
                )
            )

        return rules

    @staticmethod
    def __get_global_rules() -> list[CleanupRule]:
        """
        Retorna as regras globais.
        """

        return [
            #
            # ====================================================
            # Arquivos
            # ====================================================
            #

            CleanupRule(
                target=CleanupTarget.FILE,
                pattern="*.pdb",
                action=CleanupAction.REMOVE,
                description=(
                    "Remove arquivos de símbolos "
                    "de debug."
                ),
            ),

            CleanupRule(
                target=CleanupTarget.FILE,
                pattern="*.xml",
                action=CleanupAction.REMOVE,
                description=(
                    "Remove arquivos XML gerados "
                    "pelo Build."
                ),
            ),

            CleanupRule(
                target=CleanupTarget.FILE,
                pattern="*.config",
                action=CleanupAction.REMOVE,
                description=(
                    "Remove arquivos de configuração "
                    "gerados pelo Build."
                ),
            ),

            #
            # ====================================================
            # Diretórios
            # ====================================================
            #
            # Por padrão, todos os diretórios do resultado
            # do Build são removidos.
            #
            # Projetos podem preservar diretórios específicos
            # através de regras PRESERVE.
            #
            # Exemplo:
            #
            #     Movement
            #         XML -> PRESERVE
            #
            # ====================================================
            #

            CleanupRule(
                target=CleanupTarget.DIRECTORY,
                pattern="*",
                action=CleanupAction.REMOVE,
                description=(
                    "Remove diretórios do resultado "
                    "do Build. Diretórios necessários "
                    "devem ser preservados através "
                    "de uma regra específica do projeto."
                ),
            ),
        ]

    @staticmethod
    def __get_project_rules(
        project_id: str,
    ) -> list[CleanupRule]:
        """
        Retorna regras específicas do projeto.
        """

        rules: list[CleanupRule] = []

        #
        # ========================================================
        # LinkPagamento
        # ========================================================
        #

        if project_id == "linkpagamento":

            rules.append(
                CleanupRule(
                    target=CleanupTarget.FILE,
                    pattern=(
                        "OuroNetWinServiceLinkPagamento.exe.config"
                    ),
                    action=CleanupAction.PRESERVE,
                    project_id=project_id,
                    description=(
                        "Preserva o arquivo de configuração "
                        "principal do Windows Service."
                    ),
                )
            )

        #
        # ========================================================
        # Movement
        # ========================================================
        #

        if project_id == "movement":

            rules.append(
                CleanupRule(
                    target=CleanupTarget.DIRECTORY,
                    pattern="XML",
                    action=CleanupAction.PRESERVE,
                    project_id=project_id,
                    description=(
                        "Preserva a pasta XML utilizada "
                        "pelo WCF Movement."
                    ),
                )
            )

        return rules