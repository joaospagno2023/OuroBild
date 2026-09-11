"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : sql_cleanup_rule_repository.py
Descrição : Repositório SQL Server das regras de limpeza.
--------------------------------------------------------------------
"""

from sqlalchemy import (
    select,
)

from app.database.connection import (
    DatabaseConnection,
)

from app.database.models.cleanup_rule_model import (
    CleanupRuleModel,
)

from app.models.cleanup.cleanup_rule import (
    CleanupAction,
    CleanupRule,
    CleanupTarget,
)


class SqlCleanupRuleRepository:
    """
    Implementação do repositório de regras de limpeza.
    """

    def __init__(
        self,
        database_connection: DatabaseConnection,
    ) -> None:
        """
        Inicializa o repositório.
        """

        if database_connection is None:
            raise ValueError(
                "DatabaseConnection não foi informado."
            )

        self.__database_connection = (
            database_connection
        )

    def get_all_by_project(
        self,
        project_id: str,
    ) -> list[CleanupRule]:
        """
        Retorna as regras específicas de um projeto.
        """

        if not project_id:
            raise ValueError(
                "ProjectId não foi informado."
            )

        with self.__database_connection.create_session() as session:
            statement = (
                select(CleanupRuleModel)
                .where(
                    CleanupRuleModel.project_id
                    == project_id,
                )
                .order_by(
                    CleanupRuleModel.priority,
                    CleanupRuleModel.id,
                )
            )

            models = (
                session.scalars(
                    statement,
                )
                .all()
            )

            return [
                self.__to_cleanup_rule(
                    model,
                )
                for model in models
            ]

    def get_by_id(
        self,
        rule_id: int,
    ) -> CleanupRule | None:
        """
        Retorna uma regra pelo identificador.
        """

        if rule_id <= 0:
            raise ValueError(
                "CleanupRuleId inválido."
            )

        with self.__database_connection.create_session() as session:
            statement = (
                select(CleanupRuleModel)
                .where(
                    CleanupRuleModel.id
                    == rule_id,
                )
            )

            model = (
                session.scalars(
                    statement,
                )
                .first()
            )

            if model is None:
                return None

            return self.__to_cleanup_rule(
                model,
            )

    def get_next_priority(
        self,
        project_id: str,
    ) -> int:
        """
        Retorna a próxima prioridade disponível
        para as regras do projeto.
        """

        rules = self.get_all_by_project(
            project_id,
        )

        if not rules:
            return 200

        return (
            max(
                rule.priority
                for rule in rules
            )
            + 10
        )

    def create(
        self,
        rule: CleanupRule,
    ) -> CleanupRule:
        """
        Cria uma regra.
        """

        if rule is None:
            raise ValueError(
                "CleanupRule não foi informado."
            )

        if not rule.project_id:
            raise ValueError(
                "ProjectId não foi informado."
            )

        model = CleanupRuleModel(
            project_id=rule.project_id,
            target=rule.target.value,
            pattern=rule.pattern,
            action=rule.action.value,
            recursive=rule.recursive,
            description=rule.description,
            priority=rule.priority,
            enabled=rule.enabled,
        )

        with self.__database_connection.create_session() as session:
            session.add(
                model,
            )

            session.flush()

            result = (
                self.__to_cleanup_rule(
                    model,
                )
            )

            session.commit()

            return result

    def update(
        self,
        rule_id: int,
        rule: CleanupRule,
    ) -> CleanupRule:
        """
        Atualiza uma regra específica.
        """

        if rule_id <= 0:
            raise ValueError(
                "CleanupRuleId inválido."
            )

        if rule is None:
            raise ValueError(
                "CleanupRule não foi informado."
            )

        with self.__database_connection.create_session() as session:
            statement = (
                select(CleanupRuleModel)
                .where(
                    CleanupRuleModel.id
                    == rule_id,
                )
            )

            model = (
                session.scalars(
                    statement,
                )
                .first()
            )

            if model is None:
                raise ValueError(
                    "Regra de limpeza não encontrada."
                )

            if model.project_id != rule.project_id:
                raise ValueError(
                    "Regra de limpeza não pertence ao projeto."
                )

            model.target = (
                rule.target.value
            )

            model.pattern = rule.pattern

            model.action = (
                rule.action.value
            )

            model.recursive = (
                rule.recursive
            )

            model.description = (
                rule.description
            )

            model.priority = (
                rule.priority
            )

            model.enabled = (
                rule.enabled
            )

            session.flush()

            result = (
                self.__to_cleanup_rule(
                    model,
                )
            )

            session.commit()

            return result

    def delete(
        self,
        rule_id: int,
        project_id: str,
    ) -> None:
        """
        Exclui uma regra específica de projeto.
        """

        if rule_id <= 0:
            raise ValueError(
                "CleanupRuleId inválido."
            )

        if not project_id:
            raise ValueError(
                "ProjectId não foi informado."
            )

        with self.__database_connection.create_session() as session:
            statement = (
                select(CleanupRuleModel)
                .where(
                    CleanupRuleModel.id
                    == rule_id,
                )
            )

            model = (
                session.scalars(
                    statement,
                )
                .first()
            )

            if model is None:
                raise ValueError(
                    "Regra de limpeza não encontrada."
                )

            if model.project_id != project_id:
                raise ValueError(
                    "Regra de limpeza não pertence ao projeto."
                )

            if model.project_id is None:
                raise ValueError(
                    "Regras globais não podem ser excluídas por esta operação."
                )

            session.delete(
                model,
            )

            session.commit()

    @staticmethod
    def __to_cleanup_rule(
        model: CleanupRuleModel,
    ) -> CleanupRule:
        """
        Converte o modelo SQLAlchemy em modelo de domínio.
        """

        return CleanupRule(
            id=model.id,
            project_id=model.project_id,
            target=CleanupTarget(
                model.target,
            ),
            pattern=model.pattern,
            action=CleanupAction(
                model.action,
            ),
            recursive=model.recursive,
            description=model.description,
            priority=model.priority,
            enabled=model.enabled,
        )