"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_framework_analyzer.py
Descrição : Testes do FrameworkAnalyzer.
--------------------------------------------------------------------
"""

from pathlib import Path
from xml.etree.ElementTree import fromstring

from app.analyzers.framework_analyzer import (
    FrameworkAnalyzer,
)
from app.models.analyzers.project_document import (
    ProjectDocument,
)


def test_should_analyze_framework():
    """
    Deve analisar corretamente
    o framework do projeto.
    """

    #
    # Arrange
    #

    xml = """
<Project Sdk="Microsoft.NET.Sdk">

    <PropertyGroup>

        <TargetFramework>net9.0</TargetFramework>

    </PropertyGroup>

</Project>
"""

    document = ProjectDocument(
        file_path=Path("MeuProjeto.csproj"),
        root=fromstring(xml),
    )

    analyzer = FrameworkAnalyzer()

    #
    # Act
    #

    profile = analyzer.analyze(
        document=document,
    )

    #
    # Assert
    #

    assert profile.target_framework == "net9.0"

    assert profile.target_framework_version == ""

    assert profile.sdk_style is True

    assert profile.tools_version == ""


def test_should_analyze_legacy_framework():
    """
    Deve analisar corretamente
    um projeto legado.
    """

    #
    # Arrange
    #

    xml = """
<Project ToolsVersion="15.0">

    <PropertyGroup>

        <TargetFrameworkVersion>v4.8</TargetFrameworkVersion>

    </PropertyGroup>

</Project>
"""

    document = ProjectDocument(
        file_path=Path("Legacy.csproj"),
        root=fromstring(xml),
    )

    analyzer = FrameworkAnalyzer()

    #
    # Act
    #

    profile = analyzer.analyze(
        document=document,
    )

    #
    # Assert
    #

    assert profile.target_framework == ""

    assert profile.target_framework_version == "v4.8"

    assert profile.sdk_style is False

    assert profile.tools_version == "15.0"