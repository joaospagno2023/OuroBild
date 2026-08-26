"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_artifact_cleanup_factory.py
Descrição : Cria o serviço de limpeza com a política do projeto.
--------------------------------------------------------------------
"""

from app.services.cleanup.build_artifact_cleanup_service import (
    BuildArtifactCleanupService,
)

from app.services.cleanup.cleanup_rules_provider import (
    CleanupRulesProvider,
)


class BuildArtifactCleanupFactory:
    """
    Cria BuildArtifactCleanupService utilizando
    as regras oficiais do OuroBuild.
    """

    @staticmethod
    def create(
        project_id: str | None = None,
    ) -> BuildArtifactCleanupService:
        """
        Cria o serviço configurado para o projeto.
        """

        rules = (
            CleanupRulesProvider.get_rules(
                project_id=project_id,
            )
        )

        return BuildArtifactCleanupService(
            rules=rules,
        )