"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_excluir_pasta_work.py
Descrição : Testes da configuração de exclusão do workspace.
--------------------------------------------------------------------
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.models.setup.setup_engine import SetupEngine
from app.models.configuration.setup_settings import SetupSettings
from app.services.setup.advanced_installer_workspace_service import (
    AdvancedInstallerWorkspaceService,
)
from app.services.setup.advanced_installer_service import (
    AdvancedInstallerService,
)


def create_settings(
    excluirpastawork: bool = False,
) -> SetupSettings:
    return SetupSettings(
        engine=SetupEngine.ADVANCED_INSTALLER,
        output_root=Path(r"C:\Setups"),
        aip_root=Path(
            r"C:\DvpLocal\WorkSpaceTFS"
            r"\Transferencia de Arquivo"
            r"\TransferenciaDeArquivos"
            r"\Setups\Installers\Projects"
        ),
        excluirpastawork=excluirpastawork,
    )


def test_setup_settings_deve_usar_false_por_padrao():
    settings = create_settings()

    assert settings.excluirpastawork is False


def test_setup_settings_deve_aceitar_true():
    settings = create_settings(
        excluirpastawork=True,
    )

    assert settings.excluirpastawork is True


def test_workspace_service_cleanup_remove_workspace(
    tmp_path: Path,
):
    service = AdvancedInstallerWorkspaceService(
        workspace_root=tmp_path / ".work",
    )

    workspace = service.create(
        project_id="teste",
    )

    (workspace / "arquivo.txt").write_text(
        "teste",
        encoding="utf-8",
    )

    service.cleanup(
        workspace_path=workspace,
    )

    assert not workspace.exists()


def test_advanced_installer_service_deve_receber_flag(
    tmp_path: Path,
):
    process_service = MagicMock()
    cleanup_factory = MagicMock()
    aip_synchronizer = MagicMock()
    workspace_service = AdvancedInstallerWorkspaceService(
        workspace_root=tmp_path / ".work",
    )

    advanced_installer_path = (
        tmp_path / "AdvancedInstaller.com"
    )
    advanced_installer_path.write_text(
        "",
        encoding="utf-8",
    )

    service = AdvancedInstallerService(
        process_service=process_service,
        advanced_installer_path=advanced_installer_path,
        cleanup_factory=cleanup_factory,
        aip_synchronizer=aip_synchronizer,
        workspace_service=workspace_service,
        excluirpastawork=False,
    )

    assert service is not None


def test_advanced_installer_service_deve_rejeitar_flag_invalida(
    tmp_path: Path,
):
    process_service = MagicMock()
    cleanup_factory = MagicMock()
    aip_synchronizer = MagicMock()
    workspace_service = AdvancedInstallerWorkspaceService(
        workspace_root=tmp_path / ".work",
    )

    advanced_installer_path = (
        tmp_path / "AdvancedInstaller.com"
    )
    advanced_installer_path.write_text(
        "",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="ExcluirPastawork deve ser booleano.",
    ):
        AdvancedInstallerService(
            process_service=process_service,
            advanced_installer_path=advanced_installer_path,
            cleanup_factory=cleanup_factory,
            aip_synchronizer=aip_synchronizer,
            workspace_service=workspace_service,
            excluirpastawork="sim",
        )
