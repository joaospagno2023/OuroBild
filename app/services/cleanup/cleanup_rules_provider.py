"""
Provider das regras de limpeza de artefatos.

As regras globais permanecem definidas pelo sistema.

As regras específicas de cada projeto são obtidas exclusivamente
através do SqlCleanupRuleRepository.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.models.cleanup.cleanup_rule import (
    CleanupAction,
    CleanupRule,
    CleanupTarget,
)

if TYPE_CHECKING:
    from app.repositories.sql_cleanup_rule_repository import (
        SqlCleanupRuleRepository,
    )


class CleanupRulesProvider:
    """
    Fornece as regras utilizadas pelo processo de limpeza.

    Regras globais:
        - Arquivos: remove tudo.
        - Arquivos *.dll: preserva.
        - Diretórios: remove tudo.

    Regras específicas:
        - Obtidas exclusivamente do banco de dados por meio do
          SqlCleanupRuleRepository.
    """

    __repository: SqlCleanupRuleRepository | None = None

    @classmethod
    def configure(
        cls,
        repository: SqlCleanupRuleRepository,
    ) -> None:
        """
        Configura o repositório utilizado para carregar as regras
        específicas dos projetos.

        Args:
            repository: Repositório de regras de limpeza.
        """
        if repository is None:
            raise ValueError(
                "SqlCleanupRuleRepository não foi informado."
            )

        cls.__repository = repository

    @classmethod
    def clear_configuration(cls) -> None:
        """
        Remove a configuração atual do repositório.

        Útil principalmente para testes.
        """
        cls.__repository = None

    @classmethod
    def get_rules(
        cls,
        project_id: str | None = None,
    ) -> list[CleanupRule]:
        """
        Retorna as regras de limpeza.

        As regras globais são sempre carregadas.

        Quando um project_id é informado, as regras específicas
        são carregadas do banco de dados.

        Apenas regras habilitadas são retornadas.
        """
        rules = cls.__get_global_rules()

        if not project_id:
            return rules

        project_rules = cls.__get_project_rules(
            project_id=project_id,
        )

        rules.extend(project_rules)

        return rules

    @staticmethod
    def __get_global_rules() -> list[CleanupRule]:
        """
        Retorna as regras globais do processo de limpeza.
        """
        return [
            CleanupRule(
                target=CleanupTarget.FILE,
                pattern="*",
                action=CleanupAction.REMOVE,
                recursive=True,
                project_id=None,
                description=(
                    "Remove todos os arquivos que não forem "
                    "explicitamente preservados."
                ),
                priority=100,
                enabled=True,
            ),
            CleanupRule(
                target=CleanupTarget.FILE,
                pattern="*.dll",
                action=CleanupAction.PRESERVE,
                recursive=True,
                project_id=None,
                description=(
                    "Preserva arquivos DLL."
                ),
                priority=110,
                enabled=True,
            ),
            CleanupRule(
                target=CleanupTarget.DIRECTORY,
                pattern="*",
                action=CleanupAction.REMOVE,
                recursive=True,
                project_id=None,
                description=(
                    "Remove todos os diretórios que não forem "
                    "explicitamente preservados."
                ),
                priority=120,
                enabled=True,
            ),
        ]

    @classmethod
    def __get_project_rules(
        cls,
        project_id: str,
    ) -> list[CleanupRule]:
        """
        Carrega as regras específicas do projeto no banco de dados.
        """
        if cls.__repository is None:
            raise RuntimeError(
                "CleanupRulesProvider não foi configurado com "
                "um SqlCleanupRuleRepository."
            )

        rules = cls.__repository.get_all_by_project(
            project_id=project_id,
        )

        return [
            rule
            for rule in rules
            if rule.enabled
        ]