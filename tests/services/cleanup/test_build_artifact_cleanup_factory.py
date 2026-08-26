"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_build_artifact_cleanup_factory.py
Descrição : Testes da fábrica do serviço de limpeza.
--------------------------------------------------------------------
"""

from app.models.cleanup.cleanup_rule import (
    CleanupAction,
    CleanupTarget,
)

from app.services.cleanup.build_artifact_cleanup_factory import (
    BuildArtifactCleanupFactory,
)


def test_deve_criar_servico_com_regras_globais():

    service = (
        BuildArtifactCleanupFactory.create()
    )

    assert service is not None


def test_deve_criar_servico_para_linkpagamento():

    service = (
        BuildArtifactCleanupFactory.create(
            project_id="linkpagamento",
        )
    )

    assert service is not None


def test_deve_criar_servico_para_movement():

    service = (
        BuildArtifactCleanupFactory.create(
            project_id="movement",
        )
    )

    assert service is not None