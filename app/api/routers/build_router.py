
"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_router.py
Descrição : Endpoint responsável pela execução completa do Build.
             Após Build e Publish, executa a geração do Setup.
--------------------------------------------------------------------
"""

from fastapi import APIRouter
from fastapi import Request

from app.models.build.build_request import (
    BuildRequest,
)
from app.models.setup.setup_request import (
    SetupRequest,
)


router = APIRouter(
    prefix="/builds",
    tags=["Builds"],
)


@router.post("")
def execute_build(
    build_request: BuildRequest,
    request: Request,
):
    """
    Executa o fluxo completo:

        1. Restore
        2. Clean
        3. Build
        4. Publish
        5. Setup

    O Setup não executa o Build novamente.
    """

    bootstrap = request.app.state.bootstrap

    #
    # ================================================================
    # Build + Publish
    # ================================================================
    #

    result = (
        bootstrap.execute_build_use_case.execute(
            build_request,
        )
    )

    #
    # ================================================================
    # Se Build ou Publish falhou, encerra aqui.
    # ================================================================
    #

    if not result.success:
        return result

    #
    # ================================================================
    # Setup
    # ================================================================
    #

    setup_request = SetupRequest(
        project_id=build_request.project_id,
        environment_id=build_request.environment_id,
        version=build_request.version,
        revision=build_request.revision,
        run_build=False,
    )

    setup_result = (
        bootstrap.execute_setup_use_case.execute(
            setup_request,
        )
    )

    #
    # ================================================================
    # Adiciona o Setup às etapas da Pipeline.
    # ================================================================
    #

    result.steps.extend(
        setup_result.steps,
    )

    #
    # ================================================================
    # Setup falhou
    # ================================================================
    #

    if not setup_result.success:

        result.success = False

        result.failed_step = "Setup"

        result.message = (
            setup_result.message
        )

        return result

    #
    # ================================================================
    # Setup concluído
    # ================================================================
    #

    if setup_result.output_msi is not None:

        result.artifacts.append(
            setup_result.output_msi,
        )

    return result
