"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_build_executor_factory_impl.py
Descrição : Testes da Factory de executores de Build.
--------------------------------------------------------------------
"""

from unittest.mock import MagicMock

import pytest

from app.models.build.compilation_engine import (
    CompilationEngine,
)

from app.services.build.build_executor_factory_impl import (
    BuildExecutorFactoryImpl,
)

from app.services.build.dotnet_build_executor_service import (
    DotnetBuildExecutorService,
)


def create_factory():
    """
    Cria uma Factory utilizando um ProcessExecutor
    simulado.
    """

    process_executor = MagicMock()

    return BuildExecutorFactoryImpl(
        process_executor_service=(
            process_executor
        ),
    )


def test_factory_deve_criar_executor_dotnet():
    """
    A engine DOTNET deve criar o executor
    DotnetBuildExecutorService.
    """

    factory = create_factory()

    executor = factory.create(
        CompilationEngine.DOTNET,
    )

    assert isinstance(
        executor,
        DotnetBuildExecutorService,
    )


def test_factory_deve_rejeitar_msbuild_ainda_nao_integrado():
    """
    MSBUILD ainda não possui executor integrado
    à Factory nesta etapa.
    """

    factory = create_factory()

    with pytest.raises(
        NotImplementedError,
        match="Executor MSBuild ainda não foi integrado",
    ):
        factory.create(
            CompilationEngine.MSBUILD,
        )


def test_factory_deve_rejeitar_engine_desconhecida():
    """
    Uma engine desconhecida deve gerar ValueError.
    """

    factory = create_factory()

    with pytest.raises(
        ValueError,
        match="Engine não suportada",
    ):
        factory.create(
            "engine_invalida",
        )