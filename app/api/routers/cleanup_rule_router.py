"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : cleanup_rule_router.py
Descrição : Endpoints das exceções de limpeza dos projetos.
--------------------------------------------------------------------
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)

from app.api.dependencies.current_user import (
    get_current_user,
)

from app.models.cleanup.cleanup_rule import (
    CleanupRule,
)

from app.models.cleanup.create_cleanup_rule_request import (
    CreateCleanupRuleRequest,
)

from app.models.cleanup.update_cleanup_rule_request import (
    UpdateCleanupRuleRequest,
)


router = APIRouter(
    prefix="/projects/{project_id}/cleanup-rules",
    tags=["Cleanup Rules"],
    dependencies=[
        Depends(get_current_user),
    ],
)


@router.get(
    "",
    response_model=list[CleanupRule],
)
def get_cleanup_rules(
    project_id: str,
    request: Request,
) -> list[CleanupRule]:
    """
    Retorna as exceções específicas do projeto.
    """

    bootstrap = (
        request.app.state.bootstrap
    )

    try:
        return (
            bootstrap.cleanup_rule_service.get_by_project(
                project_id,
            )
        )

    except ValueError as exc:
        message = str(exc)

        if message == "Projeto não encontrado.":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        ) from exc


@router.post(
    "",
    response_model=CleanupRule,
    status_code=status.HTTP_201_CREATED,
)
def create_cleanup_rule(
    project_id: str,
    request: Request,
    rule_request: CreateCleanupRuleRequest,
) -> CleanupRule:
    """
    Cria uma exceção específica para o projeto.
    """

    bootstrap = (
        request.app.state.bootstrap
    )

    try:
        return (
            bootstrap.cleanup_rule_service.create(
                project_id=project_id,
                request=rule_request,
            )
        )

    except ValueError as exc:
        message = str(exc)

        if message == "Projeto não encontrado.":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        ) from exc


@router.put(
    "/{rule_id}",
    response_model=CleanupRule,
)
def update_cleanup_rule(
    project_id: str,
    rule_id: int,
    request: Request,
    rule_request: UpdateCleanupRuleRequest,
) -> CleanupRule:
    """
    Atualiza uma exceção específica do projeto.
    """

    bootstrap = (
        request.app.state.bootstrap
    )

    try:
        return (
            bootstrap.cleanup_rule_service.update(
                project_id=project_id,
                rule_id=rule_id,
                request=rule_request,
            )
        )

    except ValueError as exc:
        message = str(exc)

        if message in (
            "Projeto não encontrado.",
            "Regra de limpeza não encontrada.",
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        ) from exc


@router.delete(
    "/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_cleanup_rule(
    project_id: str,
    rule_id: int,
    request: Request,
) -> None:
    """
    Exclui uma exceção específica do projeto.
    """

    bootstrap = (
        request.app.state.bootstrap
    )

    try:
        bootstrap.cleanup_rule_service.delete(
            project_id=project_id,
            rule_id=rule_id,
        )

    except ValueError as exc:
        message = str(exc)

        if message in (
            "Projeto não encontrado.",
            "Regra de limpeza não encontrada.",
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        ) from exc