"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : cleanup_rule_service.py
Descrição : Serviço de regras específicas de limpeza.
--------------------------------------------------------------------
"""

from app.models.cleanup.cleanup_rule import (
    CleanupRule,
)

from app.models.cleanup.create_cleanup_rule_request import (
    CreateCleanupRuleRequest,
)

from app.models.cleanup.update_cleanup_rule_request import (
    UpdateCleanupRuleRequest,
)

from app.repositories.sql_cleanup_rule_repository import (
    SqlCleanupRuleRepository,
)

from app.services.project_service import (
    ProjectService,
)


class CleanupRuleService:
    """
    Executa as regras de negócio relacionadas
    às exceções de limpeza.
    """

    def __init__(
        self,
        cleanup_rule_repository: SqlCleanupRuleRepository,
        project_service: ProjectService,
    ) -> None:
        """
        Inicializa o serviço.
        """

        if cleanup_rule_repository is None:
            raise ValueError(
                "CleanupRuleRepository não foi informado."
            )

        if project_service is None:
            raise ValueError(
                "ProjectService não foi informado."
            )

        self.__cleanup_rule_repository = (
            cleanup_rule_repository
        )

        self.__project_service = (
            project_service
        )

    def get_by_project(
        self,
        project_id: str,
    ) -> list[CleanupRule]:
        """
        Retorna as regras específicas de um projeto.
        """

        self.__validate_project(
            project_id,
        )

        return (
            self.__cleanup_rule_repository.get_all_by_project(
                project_id,
            )
        )

    def create(
        self,
        project_id: str,
        request: CreateCleanupRuleRequest,
    ) -> CleanupRule:
        """
        Cria uma nova exceção para o projeto.
        """

        self.__validate_project(
            project_id,
        )

        if request is None:
            raise ValueError(
                "CreateCleanupRuleRequest não foi informado."
            )

        pattern = (
            request.pattern.strip()
        )

        if not pattern:
            raise ValueError(
                "Pattern não foi informado."
            )

        priority = (
            self.__cleanup_rule_repository.get_next_priority(
                project_id,
            )
        )

        rule = CleanupRule(
            project_id=project_id,
            target=request.target,
            pattern=pattern,
            action=request.action,
            recursive=request.recursive,
            description=(
                request.description.strip()
                if request.description
                else None
            ),
            priority=priority,
            enabled=request.enabled,
        )

        return (
            self.__cleanup_rule_repository.create(
                rule,
            )
        )

    def update(
        self,
        project_id: str,
        rule_id: int,
        request: UpdateCleanupRuleRequest,
    ) -> CleanupRule:
        """
        Atualiza uma exceção do projeto.
        """

        self.__validate_project(
            project_id,
        )

        if request is None:
            raise ValueError(
                "UpdateCleanupRuleRequest não foi informado."
            )

        existing = (
            self.__cleanup_rule_repository.get_by_id(
                rule_id,
            )
        )

        if existing is None:
            raise ValueError(
                "Regra de limpeza não encontrada."
            )

        if existing.project_id != project_id:
            raise ValueError(
                "Regra de limpeza não pertence ao projeto."
            )

        pattern = (
            request.pattern.strip()
        )

        if not pattern:
            raise ValueError(
                "Pattern não foi informado."
            )

        rule = CleanupRule(
            id=rule_id,
            project_id=project_id,
            target=request.target,
            pattern=pattern,
            action=request.action,
            recursive=request.recursive,
            description=(
                request.description.strip()
                if request.description
                else None
            ),
            priority=existing.priority,
            enabled=request.enabled,
        )

        return (
            self.__cleanup_rule_repository.update(
                rule_id,
                rule,
            )
        )

    def delete(
        self,
        project_id: str,
        rule_id: int,
    ) -> None:
        """
        Exclui uma exceção do projeto.
        """

        self.__validate_project(
            project_id,
        )

        existing = (
            self.__cleanup_rule_repository.get_by_id(
                rule_id,
            )
        )

        if existing is None:
            raise ValueError(
                "Regra de limpeza não encontrada."
            )

        if existing.project_id != project_id:
            raise ValueError(
                "Regra de limpeza não pertence ao projeto."
            )

        self.__cleanup_rule_repository.delete(
            rule_id,
            project_id,
        )

    def __validate_project(
        self,
        project_id: str,
    ) -> None:
        """
        Confirma que o projeto existe.
        """

        if not project_id:
            raise ValueError(
                "ProjectId não foi informado."
            )

        project = (
            self.__project_service.get_by_id(
                project_id,
            )
        )

        if project is None:
            raise ValueError(
                "Projeto não encontrado."
            )