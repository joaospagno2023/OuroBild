"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_network_setup_publisher.py
Descrição : Testes da publicação de Setup na rede.
--------------------------------------------------------------------
"""

from pathlib import Path

import pytest

import app.services.setup.network_setup_publisher as network_publisher_module
from app.models.configuration.app_settings import AppSettings
from app.services.setup.network_setup_publisher import (
    DefaultSetupNetworkPublisher,
)


def create_settings(
    network_root: Path,
) -> AppSettings:
    """
    Cria uma configuração mínima para os testes.

    O publisher utiliza somente:
        settings.setup.network_root_path

    O model_construct permite montar o AppSettings sem
    precisar fornecer configurações que não participam
    destes testes.
    """

    setup_settings = type(
        "SetupSettingsStub",
        (),
        {
            "network_root_path": network_root,
        },
    )()

    return AppSettings.model_construct(
        setup=setup_settings,
    )


def create_source(
    source_root: Path,
    client_folder: str = "Client",
) -> Path:
    """
    Cria uma estrutura mínima de Setup.
    """

    client_path = source_root / client_folder
    server_path = source_root / "Server"

    client_path.mkdir(
        parents=True,
    )

    server_path.mkdir(
        parents=True,
    )

    (
        client_path / "client.msi"
    ).write_text(
        "client",
        encoding="utf-8",
    )

    (
        server_path / "server.msi"
    ).write_text(
        "server",
        encoding="utf-8",
    )

    return source_root


def get_destination(
    network_root: Path,
) -> Path:
    """
    Retorna o destino esperado para a versão
    10.4.7.2.
    """

    return (
        network_root
        / "10.4"
        / "10.4.7"
    )


def test_publish_new_setup(
    tmp_path: Path,
) -> None:
    """
    Deve publicar um Setup novo na rede.
    """

    network_root = tmp_path / "network" / "Setups"
    source_root = tmp_path / "10.4.7.2"

    network_root.mkdir(parents=True)

    create_source(
        source_root,
    )

    settings = create_settings(
        network_root,
    )

    publisher = DefaultSetupNetworkPublisher(
        settings,
    )

    result = publisher.publish(
        project_id="project-001",
        source_path=source_root,
        version="10.4.7",
        revision=2,
    )

    destination = get_destination(
        network_root,
    )

    assert result.success is True
    assert result.project_id == "project-001"
    assert result.source_path == source_root
    assert result.destination_path == destination
    assert result.backup_created is False
    assert result.backup_removed is False
    assert result.files_copied == 2

    assert (
        destination
        / "Client"
        / "client.msi"
    ).exists()

    assert (
        destination
        / "Server"
        / "server.msi"
    ).exists()


def test_publish_existing_setup_creates_backup(
    tmp_path: Path,
) -> None:
    """
    Deve criar backup quando o destino já existir
    e removê-lo após publicação bem-sucedida.
    """

    network_root = tmp_path / "network" / "Setups"
    source_root = tmp_path / "10.4.7.2"

    network_root.mkdir(parents=True)

    create_source(
        source_root,
    )

    destination = get_destination(
        network_root,
    )

    old_client = destination / "Client"

    old_client.mkdir(
        parents=True,
    )

    (
        old_client / "old.txt"
    ).write_text(
        "versao anterior",
        encoding="utf-8",
    )

    settings = create_settings(
        network_root,
    )

    publisher = DefaultSetupNetworkPublisher(
        settings,
    )

    result = publisher.publish(
        project_id="project-001",
        source_path=source_root,
        version="10.4.7",
        revision=2,
    )

    assert result.success is True
    assert result.backup_created is True
    assert result.backup_removed is True
    assert result.backup_path is not None

    assert not result.backup_path.exists()

    assert (
        destination
        / "Client"
        / "client.msi"
    ).exists()

    assert (
        destination
        / "Server"
        / "server.msi"
    ).exists()

    assert not (
        destination
        / "Client"
        / "old.txt"
    ).exists()


def test_publish_failure_keeps_backup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Em caso de falha durante a cópia, deve remover
    o destino parcial e manter o backup.
    """

    network_root = tmp_path / "network" / "Setups"
    source_root = tmp_path / "10.4.7.2"

    network_root.mkdir(parents=True)

    create_source(
        source_root,
    )

    destination = get_destination(
        network_root,
    )

    old_client = destination / "Client"

    old_client.mkdir(
        parents=True,
    )

    (
        old_client / "old.txt"
    ).write_text(
        "versao anterior",
        encoding="utf-8",
    )

    original_copytree = (
        network_publisher_module.copytree
    )

    def failing_copytree(
        source: Path,
        destination: Path,
        *args,
        **kwargs,
    ):
        if destination.name == "Server":
            raise OSError(
                "Arquivo do Server em uso."
            )

        return original_copytree(
            source,
            destination,
            *args,
            **kwargs,
        )

    monkeypatch.setattr(
        network_publisher_module,
        "copytree",
        failing_copytree,
    )

    settings = create_settings(
        network_root,
    )

    publisher = DefaultSetupNetworkPublisher(
        settings,
    )

    result = publisher.publish(
        project_id="project-001",
        source_path=source_root,
        version="10.4.7",
        revision=2,
    )

    assert result.success is False
    assert result.backup_created is True
    assert result.backup_removed is False
    assert result.backup_path is not None

    assert result.backup_path.exists()
    assert not destination.exists()

    assert (
        result.backup_path
        / "Client"
        / "old.txt"
    ).exists()


def test_publish_accepts_cliente_source_folder(
    tmp_path: Path,
) -> None:
    """
    Deve aceitar a estrutura local Cliente e publicar
    como Client na rede.
    """

    network_root = tmp_path / "network" / "Setups"
    source_root = tmp_path / "10.4.7.2"

    network_root.mkdir(parents=True)

    create_source(
        source_root,
        client_folder="Cliente",
    )

    settings = create_settings(
        network_root,
    )

    publisher = DefaultSetupNetworkPublisher(
        settings,
    )

    result = publisher.publish(
        project_id="project-001",
        source_path=source_root,
        version="10.4.7",
        revision=2,
    )

    destination = get_destination(
        network_root,
    )

    assert result.success is True

    assert (
        destination
        / "Client"
        / "client.msi"
    ).exists()

    assert (
        destination
        / "Server"
        / "server.msi"
    ).exists()

    assert not (
        destination
        / "Cliente"
    ).exists()


def test_publish_fails_when_server_is_missing(
    tmp_path: Path,
) -> None:
    """
    Não deve publicar quando Server não existir.
    """

    network_root = tmp_path / "network" / "Setups"
    source_root = tmp_path / "10.4.7.2"

    network_root.mkdir(parents=True)

    client_path = source_root / "Client"

    client_path.mkdir(
        parents=True,
    )

    (
        client_path / "client.msi"
    ).write_text(
        "client",
        encoding="utf-8",
    )

    settings = create_settings(
        network_root,
    )

    publisher = DefaultSetupNetworkPublisher(
        settings,
    )

    result = publisher.publish(
        project_id="project-001",
        source_path=source_root,
        version="10.4.7",
        revision=2,
    )

    destination = get_destination(
        network_root,
    )

    assert result.success is False
    assert not destination.exists()


def test_publish_fails_when_source_is_missing(
    tmp_path: Path,
) -> None:
    """
    Não deve alterar a rede quando a origem não existir.
    """

    network_root = tmp_path / "network" / "Setups"
    source_root = tmp_path / "10.4.7.2"

    network_root.mkdir(parents=True)

    settings = create_settings(
        network_root,
    )

    publisher = DefaultSetupNetworkPublisher(
        settings,
    )

    result = publisher.publish(
        project_id="project-001",
        source_path=source_root,
        version="10.4.7",
        revision=2,
    )

    destination = get_destination(
        network_root,
    )

    assert result.success is False
    assert not destination.exists()


def test_publish_fails_with_invalid_version(
    tmp_path: Path,
) -> None:
    """
    Não deve publicar quando a versão não possuir
    pelo menos três componentes.
    """

    network_root = tmp_path / "network" / "Setups"
    source_root = tmp_path / "10"

    network_root.mkdir(parents=True)

    create_source(
        source_root,
    )

    settings = create_settings(
        network_root,
    )

    publisher = DefaultSetupNetworkPublisher(
        settings,
    )

    result = publisher.publish(
        project_id="project-001",
        source_path=source_root,
        version="10",
        revision=2,
    )

    assert result.success is False

    assert list(
        network_root.iterdir()
    ) == []