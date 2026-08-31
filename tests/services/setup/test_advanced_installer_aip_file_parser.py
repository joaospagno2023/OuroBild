"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_advanced_installer_aip_file_parser.py
Descrição : Testes do parser de arquivos do Advanced Installer.
--------------------------------------------------------------------
"""

from pathlib import Path


from app.services.setup.advanced_installer_aip_file_parser import (
    AdvancedInstallerAipFileParser,
)


AIP_ROOT = Path(
    r"C:\DvpLocal\WorkSpaceTFS"
    r"\Transferencia de Arquivo"
    r"\TransferenciaDeArquivos"
    r"\Setups"
    r"\Installers"
    r"\Projects"
)


AIP_PATH = (
    AIP_ROOT
    / "OuroNet.WinServiceLinkPagamento.aip"
)


PUBLISH_PATH = Path(
    r"C:\DvpLocal\WorkSpaceTFS"
    r"\OuroNet"
    r"\Scc"
    r"\Producao"
    r"\OuroNet"
    r"\02-Source"
    r"\01-Client"
    r"\OuroNet.Client.WinService.LinkPagamento"
    r"\bin"
    r"\Release"
)


def test_deve_identificar_arquivos_individuais_do_aip_real():
    """
    Deve identificar os arquivos individuais existentes
    no AIP real do LinkPagamento.
    """

    if not AIP_PATH.exists():

        raise FileNotFoundError(
            "AIP do LinkPagamento não encontrado:\n"
            f"{AIP_PATH}"
        )

    content = (
        AIP_PATH.read_text(
            encoding="utf-8",
        )
    )

    parser = (
        AdvancedInstallerAipFileParser()
    )

    files = parser.parse(
        content=content,
        publish_path=PUBLISH_PATH,
    )

    assert files

    print()
    print(
        "=" * 80
    )

    print(
        "[OuroBuild] ARQUIVOS INDIVIDUAIS DO AIP"
    )

    print(
        "=" * 80
    )

    for file in files[:50]:

        print(
            f"[OuroBuild] "
            f"{file.name} "
            f"| SourcePath={file.source_path}"
        )

    print(
        "=" * 80
    )

    print(
        "[OuroBuild] Total:"
    )

    print(
        len(files)
    )

    print(
        "=" * 80
    )


def test_deve_identificar_msi_files_component():
    """
    Deve identificar arquivos dentro de um
    MsiFilesComponent.
    """

    content = """
<COMPONENT cid="caphyon.advinst.msicomp.MsiFilesComponent">
    <ROW
        File="Teste.exe"
        Component_="Teste.exe"
        FileName="TESTE~1.EXE|Teste.exe"
        Attributes="0"
        SourcePath="Teste.exe"
        SelfReg="false"/>
</COMPONENT>
"""

    parser = (
        AdvancedInstallerAipFileParser()
    )

    files = parser.parse(
        content=content,
        publish_path=Path(
            r"C:\Build"
        ),
    )

    assert len(files) == 1

    assert (
        files[0].name
        == "Teste.exe"
    )

    assert (
        files[0].source_path
        == "Teste.exe"
    )

    assert (
        files[0].publish_path
        == Path(
            r"C:\Build\Teste.exe"
        )
    )


def test_nao_deve_tratar_synchronized_folder_como_arquivo():
    """
    A SynchronizedFolderComponent nunca deve ser interpretada
    como arquivos individuais.
    """

    content = """
<COMPONENT cid="caphyon.advinst.msicomp.SynchronizedFolderComponent">
    <ROW
        SourcePath="C:\\Build"
        Destination="APPDIR"
        Flags="1"
        Component="SynchronizedFolderComponent"/>
</COMPONENT>
"""

    parser = (
        AdvancedInstallerAipFileParser()
    )

    files = parser.parse(
        content=content,
        publish_path=Path(
            r"C:\Build"
        ),
    )

    assert files == []


def test_nao_deve_considerar_outros_componentes():
    """
    Componentes que não são MsiFilesComponent não devem
    ser tratados como arquivos individuais.
    """

    content = """
<COMPONENT cid="caphyon.advinst.msicomp.ShortcutsComponent">
    <ROW
        File="Teste.exe"
        Component_="Teste.exe"
        SourcePath="Teste.exe"/>
</COMPONENT>
"""

    parser = (
        AdvancedInstallerAipFileParser()
    )

    files = parser.parse(
        content=content,
        publish_path=Path(
            r"C:\Build"
        ),
    )

    assert files == []


def test_deve_normalizar_source_path_com_subdiretorio():
    """
    Deve obter corretamente o nome físico do arquivo quando
    SourcePath possui subdiretórios.
    """

    content = """
<COMPONENT cid="caphyon.advinst.msicomp.MsiFilesComponent">
    <ROW
        File="Biblioteca.dll"
        Component_="Biblioteca.dll"
        FileName="BIBLIO~1.DLL|Biblioteca.dll"
        Attributes="0"
        SourcePath="x64\\Biblioteca.dll"
        SelfReg="false"/>
</COMPONENT>
"""

    parser = (
        AdvancedInstallerAipFileParser()
    )

    files = parser.parse(
        content=content,
        publish_path=Path(
            r"C:\Build"
        ),
    )

    assert len(files) == 1

    assert (
        files[0].name
        == "Biblioteca.dll"
    )

    assert (
        files[0].source_path
        == r"x64\Biblioteca.dll"
    )

    assert (
        files[0].publish_path
        == Path(
            r"C:\Build\x64\Biblioteca.dll"
        )
    )