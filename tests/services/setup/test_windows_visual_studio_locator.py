"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_windows_visual_studio_locator.py
Descrição : Testes do WindowsVisualStudioLocator.
--------------------------------------------------------------------
"""

from pathlib import Path

import pytest

from app.services.setup.windows_visual_studio_locator import (
    WindowsVisualStudioLocator,
)


def test_deve_localizar_visual_studio(
    tmp_path: Path,
    monkeypatch,
):
    """
    Deve localizar o devenv.com.
    """

    visual_studio_root = (
        tmp_path
        / "Microsoft Visual Studio"
        / "2022"
        / "Professional"
        / "Common7"
        / "IDE"
    )

    visual_studio_root.mkdir(
        parents=True,
    )

    devenv = (
        visual_studio_root
         / "devenv.com"
    )

    devenv.write_text(
        "",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        WindowsVisualStudioLocator,
        "_DEFAULT_PATHS",
        (tmp_path,),
    )

    locator = (
        WindowsVisualStudioLocator()
    )

    result = locator.locate()

    assert result == devenv


def test_deve_rejeitar_visual_studio_inexistente(
    tmp_path: Path,
    monkeypatch,
):
    """
    Deve informar erro quando o Visual Studio
    não estiver instalado nos caminhos procurados.
    """

    monkeypatch.setattr(
        WindowsVisualStudioLocator,
        "_DEFAULT_PATHS",
        (
            tmp_path
            / "VisualStudio"
        ,),
    )

    locator = (
        WindowsVisualStudioLocator()
    )

    with pytest.raises(
        FileNotFoundError,
        match="devenv.com",
    ):
        locator.locate()