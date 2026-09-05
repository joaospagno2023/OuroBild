"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_permission_service.py
Descrição : Testes unitários do PermissionService.
--------------------------------------------------------------------
"""

import pytest

from app.services.authorization.permission_service import (
    PermissionService,
)


class FakePermissionRepository:
    """
    Repositório falso utilizado nos testes do serviço.
    """

    def __init__(
        self,
        permissions: list[str] | None = None,
    ) -> None:
        self.permissions = permissions or []
        self.last_user_id: int | None = None
        self.last_permission_key: str | None = None

    def has_permission(
        self,
        user_id: int,
        permission_key: str,
    ) -> bool:
        self.last_user_id = user_id
        self.last_permission_key = permission_key

        return permission_key in self.permissions

    def get_permissions(
        self,
        user_id: int,
    ) -> list[str]:
        self.last_user_id = user_id

        return list(self.permissions)


def test_has_permission_deve_retornar_true_quando_usuario_possui_permissao():
    repository = FakePermissionRepository(
        permissions=[
            "setup.execute",
        ],
    )

    service = PermissionService(repository)

    result = service.has_permission(
        user_id=1,
        permission_key="setup.execute",
    )

    assert result is True
    assert repository.last_user_id == 1
    assert repository.last_permission_key == "setup.execute"


def test_has_permission_deve_retornar_false_quando_usuario_nao_possui_permissao():
    repository = FakePermissionRepository(
        permissions=[
            "history.view",
        ],
    )

    service = PermissionService(repository)

    result = service.has_permission(
        user_id=1,
        permission_key="setup.execute",
    )

    assert result is False


def test_get_permissions_deve_retornar_permissoes_do_usuario():
    permissions = [
        "dashboard.view",
        "history.view",
        "logs.view",
    ]

    repository = FakePermissionRepository(
        permissions=permissions,
    )

    service = PermissionService(repository)

    result = service.get_permissions(
        user_id=1,
    )

    assert result == permissions
    assert repository.last_user_id == 1


@pytest.mark.parametrize(
    "user_id",
    [
        0,
        -1,
    ],
)
def test_has_permission_deve_rejeitar_usuario_invalido(
    user_id: int,
):
    repository = FakePermissionRepository()
    service = PermissionService(repository)

    with pytest.raises(
        ValueError,
        match="UserId deve ser maior que zero.",
    ):
        service.has_permission(
            user_id=user_id,
            permission_key="setup.execute",
        )


def test_has_permission_deve_rejeitar_permissao_vazia():
    repository = FakePermissionRepository()
    service = PermissionService(repository)

    with pytest.raises(
        ValueError,
        match="PermissionKey não foi informado.",
    ):
        service.has_permission(
            user_id=1,
            permission_key="",
        )


def test_get_permissions_deve_rejeitar_usuario_invalido():
    repository = FakePermissionRepository()
    service = PermissionService(repository)

    with pytest.raises(
        ValueError,
        match="UserId deve ser maior que zero.",
    ):
        service.get_permissions(
            user_id=0,
        )


def test_constructor_deve_rejeitar_repositorio_nulo():
    with pytest.raises(
        ValueError,
        match="PermissionRepository não foi informado.",
    ):
        PermissionService(None)