"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_build_pipeline_definition.py
Descrição : Testes da definição da Pipeline de Build.
--------------------------------------------------------------------
"""

from unittest.mock import MagicMock

from app.models.project.project import (
    Project,
)

from app.pipeline.build_pipeline_definition import (
    BuildPipelineDefinition,
)


def create_definition():
    """
    Cria uma BuildPipelineDefinition mínima
    para os testes.
    """

    process_service = MagicMock()

    msbuild_locator = MagicMock()

    project_metadata_service = MagicMock()

    return BuildPipelineDefinition(
        process_service=process_service,
        msbuild_locator=msbuild_locator,
        project_metadata_service=(
            project_metadata_service
        ),
    )


def create_project(
    publish_profile=None,
):
    """
    Cria um Project mínimo para os testes.
    """

    return Project(
        id="teste",
        name="Projeto Teste",
        description="Projeto utilizado nos testes",
        solution_path=None,
        project_path="Projeto.csproj",
        compilation_target="project",
        compilation_engine="msbuild",
        publish_path="",
        publish_profile=publish_profile,
        aip_path="",
        output_msi="",
        network_path="",
        configuration="Release",
        platform="AnyCPU",
        enabled=True,
    )


def test_build_pipeline_sem_publish_profile_nao_deve_criar_clean():
    """
    Sem publish_profile, a Pipeline deve manter
    o comportamento atual:

    Restore -> Build -> Publish
    """

    definition = create_definition()

    project = create_project()

    steps = definition.create_steps(
        project,
    )

    names = [
        step.name
        for step in steps
    ]

    assert names == [
        "Restore",
        "Build",
        "Publish",
    ]


def test_build_pipeline_com_publish_profile_deve_criar_clean():
    """
    Com publish_profile, a Pipeline deve executar:

    Restore -> Clean -> Build -> Publish
    """

    definition = create_definition()

    project = create_project(
        publish_profile="FolderProfile",
    )

    steps = definition.create_steps(
        project,
    )

    names = [
        step.name
        for step in steps
    ]

    assert names == [
        "Restore",
        "Clean",
        "Build",
        "Publish",
    ]