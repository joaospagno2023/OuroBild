"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_setup_factory.py
Descrição : Testes do contrato SetupFactory.
--------------------------------------------------------------------
"""

import pytest

from app.abstractions.installer_service import (
    InstallerService,
)

from app.abstractions.setup_factory import (
    SetupFactory,
)

from app.models.setup.setup_definition import (
    SetupDefinition,
)

from app.models.setup.setup_engine import (
    SetupEngine,
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


def test_setup_factory_deve_ser_abstrata():
    """
    Deve impedir a instanciação direta da Factory.
    """

    with pytest.raises(
        TypeError,
    ):
        SetupFactory()


def test_implementacao_deve_respeitar_contrato():
    """
    Uma implementação concreta deve conseguir
    implementar o método create.
    """

    class FakeInstallerService(
        InstallerService,
    ):
        def install(
            self,
            request: SetupRequest,
            definition: SetupDefinition,
            paths: SetupPaths,
        ) -> SetupResult:

            return SetupResult(
                success=True,
                message="Setup gerado.",
                project_id=request.project_id,
                output_msi=paths.output_msi,
                duration_seconds=1.0,
            )

    class FakeSetupFactory(
        SetupFactory,
    ):
        def create(
            self,
            engine: SetupEngine,
        ) -> InstallerService:

            return FakeInstallerService()

    factory = FakeSetupFactory()

    service = factory.create(
        SetupEngine.VISUAL_STUDIO,
    )

    assert isinstance(
        service,
        InstallerService,
    )