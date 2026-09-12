"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_setup_output_cleanup_service.py
Descrição : Testes do serviço de preparação da pasta de saída dos
            Setups.
--------------------------------------------------------------------
"""

from pathlib import Path
from types import SimpleNamespace

from app.services.setup.setup_output_cleanup_service import (
    SetupOutputCleanupService,
)


def create_settings(output_root: Path):
    """Cria as configurações mínimas utilizadas pelo teste."""

    return SimpleNamespace(
        setup=SimpleNamespace(
            output_root=output_root,
        ),
    )


def test_deve_limpar_saida_preservando_work(tmp_path: Path):
    """
    Deve remover os itens antigos da pasta de saída sem remover `.work`.
    """

    output_root = tmp_path / "Setups"
    work_path = output_root / ".work"

    work_path.mkdir(parents=True)
    (work_path / "arquivo-preservado.txt").write_text(
        "preservar",
        encoding="utf-8",
    )

    (output_root / "setup-antigo.msi").write_text(
        "remover",
        encoding="utf-8",
    )

    old_directory = output_root / "erro-antigo"
    old_directory.mkdir()
    (old_directory / "erro.log").write_text(
        "remover",
        encoding="utf-8",
    )

    result = SetupOutputCleanupService(
        settings=create_settings(output_root),
    ).execute()

    assert result.success is True
    assert not (output_root / "setup-antigo.msi").exists()
    assert not old_directory.exists()
    assert work_path.exists()
    assert (
        work_path / "arquivo-preservado.txt"
    ).read_text(encoding="utf-8") == "preservar"


def test_deve_criar_pasta_quando_nao_existir(tmp_path: Path):
    """
    Deve criar a pasta de saída quando ela ainda não existir.
    """

    output_root = tmp_path / "Setups"

    result = SetupOutputCleanupService(
        settings=create_settings(output_root),
    ).execute()

    assert result.success is True
    assert output_root.exists()
    assert output_root.is_dir()


def test_deve_preservar_work_em_execucoes_sequenciais(tmp_path: Path):
    """
    Uma nova chamada deve continuar preservando `.work`.
    """

    output_root = tmp_path / "Setups"
    work_path = output_root / ".work"
    work_path.mkdir(parents=True)

    (work_path / "estado.txt").write_text(
        "estado",
        encoding="utf-8",
    )

    service = SetupOutputCleanupService(
        settings=create_settings(output_root),
    )

    service.execute()

    (output_root / "novo-arquivo.msi").write_text(
        "novo",
        encoding="utf-8",
    )

    service.execute()

    assert not (output_root / "novo-arquivo.msi").exists()
    assert work_path.exists()
    assert (work_path / "estado.txt").exists()
