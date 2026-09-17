from pathlib import Path
from types import SimpleNamespace

from unittest.mock import MagicMock

from app.services.configuration.configuration_service import ConfigurationService


def test_get_build_tools_status_identifica_executaveis(tmp_path: Path) -> None:
    msbuild = tmp_path / "msbuild.exe"
    advanced_installer = tmp_path / "advancedinstaller.com"
    robocopy = tmp_path / "robocopy.exe"
    tf = tmp_path / "tf.exe"

    for path in (msbuild, advanced_installer, robocopy, tf):
        path.write_text("", encoding="utf-8")

    loader = MagicMock()
    loader.load_settings.return_value = SimpleNamespace(
        build_tools=SimpleNamespace(
            msbuild_path=msbuild,
            advanced_installer_path=advanced_installer,
            robocopy_path=robocopy,
            tf_path=tf,
        )
    )

    repository = MagicMock()
    service = ConfigurationService(loader, repository)

    result = service.get_build_tools_status()

    assert all(result[name]["online"] for name in (
        "msbuild_path",
        "advanced_installer_path",
        "robocopy_path",
        "tf_path",
    ))
