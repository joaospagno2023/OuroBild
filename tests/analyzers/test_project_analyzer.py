"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_project_analyzer.py
Descrição : Testes do ProjectAnalyzer.
--------------------------------------------------------------------
"""

from pathlib import Path
from xml.etree.ElementTree import fromstring

from app.analyzers.project_analyzer import (
    ProjectAnalyzer,
)
from app.models.analyzers.project_document import (
    ProjectDocument,
)


def test_should_analyze_project():
    """
    Deve analisar corretamente
    a identidade de um projeto.
    """

    #
    # Arrange
    #

    xml = """
<Project Sdk="Microsoft.NET.Sdk">

    <PropertyGroup>

        <AssemblyName>MeuProjeto</AssemblyName>

        <RootNamespace>MeuProjeto</RootNamespace>

        <ProjectGuid>{12345678-1234-1234-1234-123456789ABC}</ProjectGuid>

        <OutputType>Exe</OutputType>

    </PropertyGroup>

</Project>
"""

    document = ProjectDocument(
        file_path=Path("MeuProjeto.csproj"),
        root=fromstring(xml),
    )

    analyzer = ProjectAnalyzer()

    #
    # Act
    #

    profile = analyzer.analyze(
        document=document,
    )

    #
    # Assert
    #

    assert profile.name == "MeuProjeto"

    assert profile.assembly_name == "MeuProjeto"

    assert profile.root_namespace == "MeuProjeto"

    assert (
        profile.project_guid
        == "{12345678-1234-1234-1234-123456789ABC}"
    )

    assert profile.output_type == "Exe"