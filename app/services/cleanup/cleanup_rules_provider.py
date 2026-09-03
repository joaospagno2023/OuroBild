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

    Entre regras globais, quando mais de uma corresponder
    ao mesmo arquivo/diretório, a última da lista prevalece.
    Por isso, exceções globais (como a preservação de DLLs)
    são declaradas após a regra genérica de remoção.
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
        Retorna as regras globais de limpeza.

        Política padrão:

            - Todos os arquivos são removidos, exceto as
              exceções globais declaradas abaixo (DLLs).
            - Todos os diretórios são removidos.

        Projetos podem preservar arquivos ou diretórios
        adicionais através de regras específicas.
        """

        return [
            #
            # ====================================================
            # Arquivos
            # ====================================================
            #

            CleanupRule(
                target=CleanupTarget.FILE,
                pattern="*",
                action=CleanupAction.REMOVE,
                description=(
                    "Remove todos os arquivos do resultado "
                    "do Build. Arquivos necessários devem "
                    "ser preservados através de uma regra "
                    "específica do projeto."
                ),
            ),

            #
            # ----------------------------------------------------
            # Exceção global: DLLs.
            #
            # DLLs são necessárias em tempo de execução para
            # praticamente todo projeto .NET. Removê-las por
            # padrão quebraria o Setup gerado. Declarada após
            # a regra "*"/REMOVE para que prevaleça sobre ela.
            # ----------------------------------------------------
            #

            CleanupRule(
                target=CleanupTarget.FILE,
                pattern="*.dll",
                action=CleanupAction.PRESERVE,
                description=(
                    "Preserva todas as DLLs do resultado "
                    "do Build, necessárias em tempo de "
                    "execução da aplicação."
                ),
            ),

            #
            # ====================================================
            # Diretórios
            # ====================================================
            #

            CleanupRule(
                target=CleanupTarget.DIRECTORY,
                pattern="*",
                action=CleanupAction.REMOVE,
                description=(
                    "Remove todos os diretórios do resultado "
                    "do Build. Diretórios necessários devem "
                    "ser preservados através de uma regra "
                    "específica do projeto."
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

            #
            # ----------------------------------------------------
            # Executável principal
            # ----------------------------------------------------
            #

            rules.append(
                CleanupRule(
                    target=CleanupTarget.FILE,
                    pattern=(
                        "OuroNetWinServiceLinkPagamento.exe"
                    ),
                    action=CleanupAction.PRESERVE,
                    project_id=project_id,
                    description=(
                        "Preserva o executável principal "
                        "do Windows Service LinkPagamento."
                    ),
                )
            )

            #
            # ----------------------------------------------------
            # Arquivo de configuração principal
            # ----------------------------------------------------
            #

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
                        "principal do Windows Service "
                        "LinkPagamento."
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