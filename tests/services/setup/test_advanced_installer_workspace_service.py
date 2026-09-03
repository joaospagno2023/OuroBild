"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_advanced_installer_workspace_service.py
Descrição : Testes do workspace temporário do Advanced Installer.
--------------------------------------------------------------------
"""

from pathlib import Path

import pytest

from app.services.setup.advanced_installer_workspace_service import (
    AdvancedInstallerWorkspaceService,
)


def test_create_creates_project_workspace(
    tmp_path: Path,
) -> None:
    workspace_root = tmp_path / ".work"

    service = AdvancedInstallerWorkspaceService(
        workspace_root=workspace_root,
    )

    result = service.create(
        project_id="linkpagamento",
    )

    assert result == (
        workspace_root
        / "linkpagamento"
    )

    assert result.exists()
    assert result.is_dir()


def test_create_removes_existing_project_workspace(
    tmp_path: Path,
) -> None:
    workspace_root = tmp_path / ".work"

    existing_workspace = (
        workspace_root
        / "linkpagamento"
    )

    existing_workspace.mkdir(
        parents=True,
    )

    old_file = (
        existing_workspace
        / "old.txt"
    )

    old_file.write_text(
        "arquivo antigo",
        encoding="utf-8",
    )

    service = AdvancedInstallerWorkspaceService(
        workspace_root=workspace_root,
    )

    result = service.create(
        project_id="linkpagamento",
    )

    assert result.exists()
    assert not old_file.exists()


def test_prepare_copies_aip_prerequisites_and_release(
    tmp_path: Path,
) -> None:
    workspace_root = tmp_path / ".work"

    source_aip = (
        tmp_path
        / "source"
        / "OuroNet.WinServiceLinkPagamento.build.aip"
    )

    source_prerequisites = (
        tmp_path
        / "source"
        / "Prerequisites"
    )

    source_release = (
        tmp_path
        / "source"
        / "Release"
    )

    source_aip.parent.mkdir(
        parents=True,
    )

    source_aip.write_text(
        "AIP TESTE",
        encoding="utf-8",
    )

    source_prerequisites.mkdir(
        parents=True,
    )

    prerequisite_file = (
        source_prerequisites
        / "dotNetFx.exe"
    )

    prerequisite_file.write_text(
        "PREREQUISITE",
        encoding="utf-8",
    )

    source_release.mkdir(
        parents=True,
    )

    release_file = (
        source_release
        / "OuroNet.exe"
    )

    release_file.write_text(
        "RELEASE",
        encoding="utf-8",
    )

    service = AdvancedInstallerWorkspaceService(
        workspace_root=workspace_root,
    )

    result = service.prepare(
        project_id="linkpagamento",
        aip_path=source_aip,
        prerequisites_path=source_prerequisites,
        publish_path=source_release,
    )

    assert result.workspace_path.exists()
    assert result.workspace_path.is_dir()

    assert result.aip_path.exists()
    assert result.aip_path.is_file()

    assert result.prerequisites_path.exists()
    assert result.prerequisites_path.is_dir()

    assert result.publish_path.exists()
    assert result.publish_path.is_dir()

    assert (
        result.aip_path.read_text(
            encoding="utf-8",
        )
        == "AIP TESTE"
    )

    assert (
        result.prerequisites_path
        / "dotNetFx.exe"
    ).read_text(
        encoding="utf-8",
    ) == "PREREQUISITE"

    assert (
        result.publish_path
        / "OuroNet.exe"
    ).read_text(
        encoding="utf-8",
    ) == "RELEASE"


def test_prepare_does_not_modify_original_files(
    tmp_path: Path,
) -> None:
    workspace_root = tmp_path / ".work"

    source_aip = (
        tmp_path
        / "source"
        / "setup.build.aip"
    )

    source_prerequisites = (
        tmp_path
        / "source"
        / "Prerequisites"
    )

    source_release = (
        tmp_path
        / "source"
        / "Release"
    )

    source_aip.parent.mkdir(
        parents=True,
    )

    source_aip.write_text(
        "ORIGINAL AIP",
        encoding="utf-8",
    )

    source_prerequisites.mkdir(
        parents=True,
    )

    (
        source_prerequisites
        / "resource.txt"
    ).write_text(
        "ORIGINAL PREREQUISITE",
        encoding="utf-8",
    )

    source_release.mkdir(
        parents=True,
    )

    (
        source_release
        / "application.exe"
    ).write_text(
        "ORIGINAL RELEASE",
        encoding="utf-8",
    )

    service = AdvancedInstallerWorkspaceService(
        workspace_root=workspace_root,
    )

    result = service.prepare(
        project_id="teste",
        aip_path=source_aip,
        prerequisites_path=source_prerequisites,
        publish_path=source_release,
    )

    result.aip_path.write_text(
        "ALTERADO",
        encoding="utf-8",
    )

    (
        result.prerequisites_path
        / "resource.txt"
    ).write_text(
        "ALTERADO",
        encoding="utf-8",
    )

    (
        result.publish_path
        / "application.exe"
    ).write_text(
        "ALTERADO",
        encoding="utf-8",
    )

    assert source_aip.read_text(
        encoding="utf-8",
    ) == "ORIGINAL AIP"

    assert (
        source_prerequisites
        / "resource.txt"
    ).read_text(
        encoding="utf-8",
    ) == "ORIGINAL PREREQUISITE"

    assert (
        source_release
        / "application.exe"
    ).read_text(
        encoding="utf-8",
    ) == "ORIGINAL RELEASE"


def test_prepare_copies_nested_release_directories(
    tmp_path: Path,
) -> None:
    workspace_root = tmp_path / ".work"

    source_aip = (
        tmp_path
        / "setup.build.aip"
    )

    source_prerequisites = (
        tmp_path
        / "Prerequisites"
    )

    source_release = (
        tmp_path
        / "Release"
    )

    source_aip.write_text(
        "AIP",
        encoding="utf-8",
    )

    source_prerequisites.mkdir()

    source_release.mkdir()

    nested = (
        source_release
        / "x64"
        / "SkiaSharp"
    )

    nested.mkdir(
        parents=True,
    )

    nested_file = (
        nested
        / "libSkiaSharp.so"
    )

    nested_file.write_text(
        "SO",
        encoding="utf-8",
    )

    service = AdvancedInstallerWorkspaceService(
        workspace_root=workspace_root,
    )

    result = service.prepare(
        project_id="teste",
        aip_path=source_aip,
        prerequisites_path=source_prerequisites,
        publish_path=source_release,
    )

    copied_file = (
        result.publish_path
        / "x64"
        / "SkiaSharp"
        / "libSkiaSharp.so"
    )

    assert copied_file.exists()

    assert copied_file.read_text(
        encoding="utf-8",
    ) == "SO"


def test_prepare_requires_aip(
    tmp_path: Path,
) -> None:
    service = AdvancedInstallerWorkspaceService(
        workspace_root=tmp_path / ".work",
    )

    prerequisites = tmp_path / "Prerequisites"
    release = tmp_path / "Release"

    prerequisites.mkdir()
    release.mkdir()

    with pytest.raises(FileNotFoundError):
        service.prepare(
            project_id="teste",
            aip_path=tmp_path / "inexistente.aip",
            prerequisites_path=prerequisites,
            publish_path=release,
        )


def test_prepare_requires_prerequisites_directory(
    tmp_path: Path,
) -> None:
    service = AdvancedInstallerWorkspaceService(
        workspace_root=tmp_path / ".work",
    )

    aip = tmp_path / "setup.aip"
    release = tmp_path / "Release"

    aip.write_text(
        "AIP",
        encoding="utf-8",
    )

    release.mkdir()

    with pytest.raises(FileNotFoundError):
        service.prepare(
            project_id="teste",
            aip_path=aip,
            prerequisites_path=(
                tmp_path / "inexistente"
            ),
            publish_path=release,
        )


def test_prepare_requires_release_directory(
    tmp_path: Path,
) -> None:
    service = AdvancedInstallerWorkspaceService(
        workspace_root=tmp_path / ".work",
    )

    aip = tmp_path / "setup.aip"
    prerequisites = tmp_path / "Prerequisites"

    aip.write_text(
        "AIP",
        encoding="utf-8",
    )

    prerequisites.mkdir()

    with pytest.raises(FileNotFoundError):
        service.prepare(
            project_id="teste",
            aip_path=aip,
            prerequisites_path=prerequisites,
            publish_path=(
                tmp_path / "inexistente"
            ),
        )


def test_cleanup_removes_project_workspace(
    tmp_path: Path,
) -> None:
    workspace_root = tmp_path / ".work"

    service = AdvancedInstallerWorkspaceService(
        workspace_root=workspace_root,
    )

    workspace = service.create(
        project_id="linkpagamento",
    )

    (
        workspace / "arquivo.txt"
    ).write_text(
        "teste",
        encoding="utf-8",
    )

    service.cleanup(
        workspace_path=workspace,
    )

    assert not workspace.exists()


def test_cleanup_root_removes_all_workspaces(
    tmp_path: Path,
) -> None:
    workspace_root = tmp_path / ".work"

    service = AdvancedInstallerWorkspaceService(
        workspace_root=workspace_root,
    )

    service.create(
        project_id="projeto1",
    )

    service.create(
        project_id="projeto2",
    )

    (
        workspace_root
        / "arquivo.txt"
    ).write_text(
        "resíduo",
        encoding="utf-8",
    )

    service.cleanup_root()

    assert workspace_root.exists()

    assert list(
        workspace_root.iterdir()
    ) == []


def test_create_requires_project_id(
    tmp_path: Path,
) -> None:
    service = AdvancedInstallerWorkspaceService(
        workspace_root=tmp_path / ".work",
    )

    with pytest.raises(ValueError):
        service.create(
            project_id="",
        )


def test_create_rejects_project_id_as_path(
    tmp_path: Path,
) -> None:
    service = AdvancedInstallerWorkspaceService(
        workspace_root=tmp_path / ".work",
    )

    with pytest.raises(ValueError):
        service.create(
            project_id="projetos/linkpagamento",
        )