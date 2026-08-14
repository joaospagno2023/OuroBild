"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_installer_service.py
Descrição : Testes do contrato InstallerService.
--------------------------------------------------------------------
"""

from pathlib import Path

import pytest

from app.abstractions.installer_service import (
    InstallerService,
)

from app.models.setup.setup_paths import (
    SetupPaths,
)

from app.models.setup.setup_request import (
    SetupRequest,
)

from app.models.setup.setup_result import (
    SetupResult,
)


def test_installer_service_deve_ser_abstrato():
    """
    Deve impedir a instanciação direta do InstallerService.
    """

    with pytest.raises(
        TypeError,
    ):
        InstallerService()


def test_implementacao_deve_respeitar_contrato():
    """
    Uma implementação concreta deve conseguir
    implementar o método install.
    """

    class FakeInstallerService(
        InstallerService,
    ):
        def install(
            self,
            request: SetupRequest,
            paths: SetupPaths,
        ) -> SetupResult:
            return SetupResult(
                success=True,
                message="Setup gerado com sucesso.",
                project_id=request.project_id,
                output_msi=paths.output_msi,
                duration_seconds=1.0,
            )

    service = FakeInstallerService()

    request = SetupRequest(
        project_id="teste",
        environment_id="teste",
    )

    paths = SetupPaths(
        publish_path=Path(
            r"C:\Temp\publish",
        ),
        aip_path=Path(
            r"C:\Temp\Setup\Teste.aip",
        ),
        output_msi=Path(
            r"C:\Temp\installer\Teste.msi",
        ),
        setup_output_path=Path(
            r"C:\Temp\installer",
        ),
    )

    result = service.install(
        request=request,
        paths=paths,
    )

    assert isinstance(
        result,
        SetupResult,
    )

    assert result.success is True

    assert result.project_id == (
        "teste"
    )

    assert result.output_msi == (
        paths.output_msi
    )