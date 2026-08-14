"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_publish_path_resolver.py
Descrição : Testes do PublishPathResolver.
--------------------------------------------------------------------
"""

from pathlib import Path

import pytest

from app.models.build.compilation_engine import (
    CompilationEngine,
)

from app.models.build.compilation_target import (
    CompilationTarget,
)

from app.models.project.project import (
    Project,
)

from app.models.project.project_type import (
    ProjectType,
)

from app.services.setup.publish_path_resolver import (
    PublishPathResolver,
)


def create_project(
    publish_path: str,
    output_msi: str = "Teste.msi",
    aip_path: str = r"Setup\Teste.aip",
) -> Project:
    """
    Cria um projeto mínimo para os testes.
    """

    return Project(
        id="teste",
        name="Projeto Teste",
        description="Projeto utilizado nos testes.",

        type=ProjectType.CLIENT,

        solution_path=None,
        project_path="Projeto.csproj",

        compilation_target=(
            CompilationTarget.PROJECT
        ),

        compilation_engine=(
            CompilationEngine.MSBUILD
        ),

        publish_path=publish_path,
        aip_path=aip_path,
        output_msi=output_msi,
        network_path="",
        configuration="Release",
        platform="AnyCPU",
        enabled=True,
    )


def test_deve_resolver_publish_path_bin():
    """
    Deve resolver corretamente um publish_path
    simples.
    """

    project = create_project(
        "bin",
    )

    resolver = PublishPathResolver()

    result = resolver.resolve(
        project=project,
        project_root=Path(
            r"C:\Projetos\OuroNet"
        ),
    )

    assert result == Path(
        r"C:\Projetos\OuroNet\bin"
    )


def test_deve_resolver_publish_path_net8():
    """
    Deve resolver corretamente um publish_path
    de um projeto .NET moderno.
    """

    project = create_project(
        r"bin\Release\net8.0\publish",
    )

    resolver = PublishPathResolver()

    result = resolver.resolve(
        project=project,
        project_root=Path(
            r"C:\Projetos\OuroNet"
        ),
    )

    assert result == Path(
        r"C:\Projetos\OuroNet"
        r"\bin\Release\net8.0\publish"
    )


def test_deve_respeitar_publish_path_absoluto():
    """
    Deve respeitar um publish_path absoluto.
    """

    project = create_project(
        r"C:\Publish\OuroNet",
    )

    resolver = PublishPathResolver()

    result = resolver.resolve(
        project=project,
        project_root=Path(
            r"C:\Projetos\OuroNet"
        ),
    )

    assert result == Path(
        r"C:\Publish\OuroNet"
    )


def test_deve_rejeitar_publish_path_vazio():
    """
    Deve rejeitar projeto sem publish_path.
    """

    project = create_project(
        "",
    )

    resolver = PublishPathResolver()

    with pytest.raises(
        ValueError,
        match="não possui publish_path configurado",
    ):
        resolver.resolve(
            project=project,
            project_root=Path(
                r"C:\Projetos\OuroNet"
            ),
        )