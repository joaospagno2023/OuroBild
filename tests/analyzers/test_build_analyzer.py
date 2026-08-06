"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_build_analyzer.py
Descrição : Testes do BuildAnalyzer.
--------------------------------------------------------------------
"""

from pathlib import Path
from xml.etree.ElementTree import fromstring

from app.analyzers.build_analyzer import (
    BuildAnalyzer,
)
from app.models.analyzers.project_document import (
    ProjectDocument,
)
from app.models.build.compilation_engine import (
    CompilationEngine,
)


def test_should_analyze_sdk_build():
    """
    Deve analisar corretamente
    um projeto SDK.
    """

    #
    # Arrange
    #

    xml = """
<Project Sdk="Microsoft.NET.Sdk">

    <PropertyGroup>

        <TargetFramework>net9.0</TargetFramework>

        <OutputType>Exe</OutputType>

        <SignAssembly>true</SignAssembly>

        <AssemblyOriginatorKeyFile>ourobuild.snk</AssemblyOriginatorKeyFile>

    </PropertyGroup>

</Project>
"""

    document = ProjectDocument(
        file_path=Path("Sdk.csproj"),
        root=fromstring(xml),
    )

    analyzer = BuildAnalyzer()

    #
    # Act
    #

    profile = analyzer.analyze(
        document=document,
    )

    #
    # Assert
    #

    assert (
        profile.compilation_engine
        == CompilationEngine.DOTNET
    )

    assert profile.output_type == "Exe"

    assert profile.sign_assembly is True

    assert (
        profile.assembly_originator_key_file
        == "ourobuild.snk"
    )


def test_should_analyze_legacy_build():
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

        <OutputType>Library</OutputType>

        <SignAssembly>false</SignAssembly>

    </PropertyGroup>

</Project>
"""

    document = ProjectDocument(
        file_path=Path("Legacy.csproj"),
        root=fromstring(xml),
    )

    analyzer = BuildAnalyzer()

    #
    # Act
    #

    profile = analyzer.analyze(
        document=document,
    )

    #
    # Assert
    #

    assert (
        profile.compilation_engine
        == CompilationEngine.MSBUILD
    )

    assert profile.output_type == "Library"

    assert profile.sign_assembly is False

    assert (
        profile.assembly_originator_key_file
        == ""
    )