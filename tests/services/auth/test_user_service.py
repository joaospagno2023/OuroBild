"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_user_service.py
Descrição : Testes unitários do serviço de usuários.
--------------------------------------------------------------------
"""

from datetime import (
    datetime,
    timezone,
)

from unittest.mock import (
    Mock,
)

import pytest

from app.models.auth.create_user_request import (
    CreateUserRequest,
)

from app.models.auth.user import (
    User,
)

from app.services.auth.user_service import (
    UserService,
)


def create_user_request() -> CreateUserRequest:
    """
    Cria uma requisição válida para os testes.
    """

    return CreateUserRequest(
        username="novo.usuario",
        display_name="Novo Usuário",
        email="novo.usuario@ouroweb.com.br",
        password="Senha@123",
        is_active=True,
    )


def create_user() -> User:
    """
    Cria um usuário válido para os testes.
    """

    created_at = datetime.now(
        timezone.utc,
    )

    return User(
        id=10,
        username="novo.usuario",
        display_name="Novo Usuário",
        email="novo.usuario@ouroweb.com.br",
        is_active=True,
        created_at=created_at,
        last_login_at=None,
    )


def create_service() -> tuple[
    UserService,
    Mock,
    Mock,
]:
    """
    Cria o serviço com dependências simuladas.
    """

    user_repository = Mock()
    password_service = Mock()

    service = UserService(
        user_repository=user_repository,
        password_service=password_service,
    )

    return (
        service,
        user_repository,
        password_service,
    )


def test_create_user_success() -> None:
    """
    Deve criar um usuário com sucesso.
    """

    (
        service,
        user_repository,
        password_service,
    ) = create_service()

    user_request = create_user_request()
    expected_user = create_user()

    user_repository.get_by_username.return_value = None

    password_service.hash.return_value = (
        "argon2$hash"
    )

    user_repository.create.return_value = (
        expected_user
    )

    result = service.create(
        user_request,
    )

    assert result == expected_user

    user_repository.get_by_username.assert_called_once_with(
        "novo.usuario",
    )

    password_service.hash.assert_called_once_with(
        "Senha@123",
    )

    user_repository.create.assert_called_once()

    repository_request = (
        user_repository.create.call_args.kwargs[
            "request"
        ]
    )

    repository_password_hash = (
        user_repository.create.call_args.kwargs[
            "password_hash"
        ]
    )

    assert (
        repository_request.username
        == "novo.usuario"
    )

    assert (
        repository_request.display_name
        == "Novo Usuário"
    )

    assert (
        repository_request.email
        == "novo.usuario@ouroweb.com.br"
    )

    assert (
        repository_request.password
        == "Senha@123"
    )

    assert (
        repository_request.is_active
        is True
    )

    assert (
        repository_password_hash
        == "argon2$hash"
    )


@pytest.mark.parametrize(
    "user_request",
    [
        CreateUserRequest(
            username="",
            display_name="Novo Usuário",
            password="Senha@123",
        ),
        CreateUserRequest(
            username="   ",
            display_name="Novo Usuário",
            password="Senha@123",
        ),
    ],
)
def test_create_user_rejects_empty_username(
    user_request: CreateUserRequest,
) -> None:
    """
    Não deve permitir username vazio.
    """

    (
        service,
        user_repository,
        password_service,
    ) = create_service()

    with pytest.raises(
        ValueError,
        match="Username não foi informado.",
    ):
        service.create(
            user_request,
        )

    user_repository.get_by_username.assert_not_called()

    password_service.hash.assert_not_called()


@pytest.mark.parametrize(
    "user_request",
    [
        CreateUserRequest(
            username="novo.usuario",
            display_name="",
            password="Senha@123",
        ),
        CreateUserRequest(
            username="novo.usuario",
            display_name="   ",
            password="Senha@123",
        ),
    ],
)
def test_create_user_rejects_empty_display_name(
    user_request: CreateUserRequest,
) -> None:
    """
    Não deve permitir nome de exibição vazio.
    """

    (
        service,
        user_repository,
        password_service,
    ) = create_service()

    with pytest.raises(
        ValueError,
        match="DisplayName não foi informado.",
    ):
        service.create(
            user_request,
        )

    user_repository.get_by_username.assert_not_called()

    password_service.hash.assert_not_called()


def test_create_user_rejects_empty_password() -> None:
    """
    Não deve permitir senha vazia.
    """

    (
        service,
        user_repository,
        password_service,
    ) = create_service()

    user_request = CreateUserRequest(
        username="novo.usuario",
        display_name="Novo Usuário",
        password="",
    )

    with pytest.raises(
        ValueError,
        match="Password não foi informado.",
    ):
        service.create(
            user_request,
        )

    user_repository.get_by_username.assert_not_called()

    password_service.hash.assert_not_called()


def test_create_user_rejects_duplicate_username() -> None:
    """
    Não deve permitir username já cadastrado.
    """

    (
        service,
        user_repository,
        password_service,
    ) = create_service()

    existing_user = Mock()

    user_repository.get_by_username.return_value = (
        existing_user
    )

    user_request = create_user_request()

    with pytest.raises(
        ValueError,
        match="Username já está cadastrado.",
    ):
        service.create(
            user_request,
        )

    user_repository.get_by_username.assert_called_once_with(
        "novo.usuario",
    )

    password_service.hash.assert_not_called()

    user_repository.create.assert_not_called()


def test_create_user_normalizes_text_fields() -> None:
    """
    Deve remover espaços extras dos campos textuais.
    """

    (
        service,
        user_repository,
        password_service,
    ) = create_service()

    expected_user = create_user()

    user_request = CreateUserRequest(
        username="  novo.usuario  ",
        display_name="  Novo Usuário  ",
        email="  novo.usuario@ouroweb.com.br  ",
        password="Senha@123",
        is_active=True,
    )

    user_repository.get_by_username.return_value = None

    password_service.hash.return_value = (
        "argon2$hash"
    )

    user_repository.create.return_value = (
        expected_user
    )

    service.create(
        user_request,
    )

    user_repository.get_by_username.assert_called_once_with(
        "novo.usuario",
    )

    repository_request = (
        user_repository.create.call_args.kwargs[
            "request"
        ]
    )

    assert (
        repository_request.username
        == "novo.usuario"
    )

    assert (
        repository_request.display_name
        == "Novo Usuário"
    )

    assert (
        repository_request.email
        == "novo.usuario@ouroweb.com.br"
    )


def test_create_user_allows_empty_email() -> None:
    """
    Deve permitir e-mail não informado.
    """

    (
        service,
        user_repository,
        password_service,
    ) = create_service()

    expected_user = create_user()

    user_request = CreateUserRequest(
        username="novo.usuario",
        display_name="Novo Usuário",
        email=None,
        password="Senha@123",
        is_active=True,
    )

    user_repository.get_by_username.return_value = None

    password_service.hash.return_value = (
        "argon2$hash"
    )

    user_repository.create.return_value = (
        expected_user
    )

    service.create(
        user_request,
    )

    repository_request = (
        user_repository.create.call_args.kwargs[
            "request"
        ]
    )

    assert (
        repository_request.email
        is None
    )


def test_create_user_rejects_none_request() -> None:
    """
    Deve rejeitar uma requisição inexistente.
    """

    (
        service,
        user_repository,
        password_service,
    ) = create_service()

    with pytest.raises(
        ValueError,
        match="CreateUserRequest não foi informado.",
    ):
        service.create(
            None,  # type: ignore[arg-type]
        )

    user_repository.get_by_username.assert_not_called()

    password_service.hash.assert_not_called()


def test_constructor_rejects_none_repository() -> None:
    """
    Deve rejeitar UserRepository inexistente.
    """

    with pytest.raises(
        ValueError,
        match="UserRepository não foi informado.",
    ):
        UserService(
            user_repository=None,  # type: ignore[arg-type]
            password_service=Mock(),
        )


def test_constructor_rejects_none_password_service() -> None:
    """
    Deve rejeitar PasswordService inexistente.
    """

    with pytest.raises(
        ValueError,
        match="PasswordService não foi informado.",
    ):
        UserService(
            user_repository=Mock(),
            password_service=None,  # type: ignore[arg-type]
        )