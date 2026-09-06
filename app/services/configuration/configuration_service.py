"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : configuration_service.py
Descrição : Responsável por ler e atualizar as configurações
             operacionais do OuroBuild.
--------------------------------------------------------------------
"""

import base64
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from app.core.configuration.configuration_loader import (
    ConfigurationLoader,
)
from app.models.configuration.app_settings import (
    AppSettings,
)
from app.models.configuration.configuration_response import (
    ConfigurationResponse,
)
from app.models.configuration.configuration_update_request import (
    ConfigurationUpdateRequest,
)


class ConfigurationService:
    """
    Responsável pelo gerenciamento da configuração operacional.
    """

    def __init__(
        self,
        configuration_loader: ConfigurationLoader,
    ) -> None:
        self._configuration_loader = (
            configuration_loader
        )

    def get_configuration(
        self,
    ) -> ConfigurationResponse:
        """
        Retorna somente as configurações editáveis.

        A seção de banco de dados e as configurações de segurança
        não são expostas pela API.
        """

        settings = (
            self._configuration_loader.load_settings()
        )

        return self._to_response(
            settings=settings,
        )

    def update_configuration(
        self,
        request: ConfigurationUpdateRequest,
    ) -> ConfigurationResponse:
        """
        Atualiza as configurações editáveis no settings.json.

        As demais propriedades existentes no arquivo são preservadas.
        """

        settings_path = self._get_settings_path()

        data = self._read_raw_configuration(
            settings_path=settings_path,
        )

        data["application_name"] = (
            request.application_name.strip()
        )

        data["version"] = (
            request.version.strip()
        )

        data["log_level"] = (
            request.log_level.strip().upper()
        )

        data["base_path"] = (
            request.base_path.strip()
        )

        data["installer_path"] = (
            request.installer_path.strip()
        )

        data["publish_path"] = (
            request.publish_path.strip()
        )

        data["storage"] = {
            "root_path": str(
                request.storage.workspace_path,
            ),
        }

        data["build_tools"] = {
            "msbuild_path": str(
                request.build_tools.msbuild_path,
            ),
            "advanced_installer_path": str(
                request.build_tools.advanced_installer_path,
            ),
            "robocopy_path": str(
                request.build_tools.robocopy_path,
            ),
        }

        data["setup"] = {
            "engine": request.setup.engine.value,
            "output_root": str(
                request.setup.output_root,
            ),
            "aip_root": str(
                request.setup.aip_root,
            ),
            "excluirpastawork": (
                request.setup.excluirpastawork
            ),
        }

        data["logging"] = {
            "enabled": request.logging.enabled,
            "path": str(
                request.logging.path,
            ),
            "level": (
                request.logging.level.upper()
            ),
        }

        self._write_raw_configuration(
            settings_path=settings_path,
            data=data,
        )

        settings = (
            self._configuration_loader.load_settings()
        )

        return self._to_response(
            settings=settings,
        )

    def browse_folder(
        self,
        initial_path: str | None = None,
    ) -> str | None:
        """
        Abre o seletor nativo de pastas do Windows.

        Retorna o caminho selecionado ou None quando o usuário
        cancela a operação.
        """

        script = self._build_folder_dialog_script(
            initial_path=initial_path,
        )

        return self._run_windows_dialog(
            script=script,
        )

    def browse_file(
        self,
        initial_path: str | None = None,
    ) -> str | None:
        """
        Abre o seletor nativo de arquivos do Windows.

        Retorna o caminho selecionado ou None quando o usuário
        cancela a operação.
        """

        script = self._build_file_dialog_script(
            initial_path=initial_path,
        )

        return self._run_windows_dialog(
            script=script,
        )

    @staticmethod
    def _build_folder_dialog_script(
        initial_path: str | None,
    ) -> str:
        """
        Monta o script PowerShell responsável por abrir o
        seletor nativo de pastas.
        """

        encoded_initial_path = (
            ConfigurationService._encode_powershell_string(
                initial_path or "",
            )
        )

        return f"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$initialPath = [System.Text.Encoding]::UTF8.GetString(
    [System.Convert]::FromBase64String("{encoded_initial_path}")
)

$dialog = New-Object System.Windows.Forms.FolderBrowserDialog
$dialog.Description = "Selecione uma pasta"
$dialog.ShowNewFolderButton = $true

if (
    $initialPath -and
    [System.IO.Directory]::Exists($initialPath)
) {{
    $dialog.SelectedPath = $initialPath
}}

$result = $dialog.ShowDialog()

if ($result -eq [System.Windows.Forms.DialogResult]::OK) {{
    Write-Output $dialog.SelectedPath
}}
"""

    @staticmethod
    def _build_file_dialog_script(
        initial_path: str | None,
    ) -> str:
        """
        Monta o script PowerShell responsável por abrir o
        seletor nativo de arquivos.
        """

        encoded_initial_path = (
            ConfigurationService._encode_powershell_string(
                initial_path or "",
            )
        )

        return f"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$initialPath = [System.Text.Encoding]::UTF8.GetString(
    [System.Convert]::FromBase64String("{encoded_initial_path}")
)

$dialog = New-Object System.Windows.Forms.OpenFileDialog
$dialog.Title = "Selecione um arquivo"
$dialog.Filter = "Todos os arquivos (*.*)|*.*"
$dialog.CheckFileExists = $true
$dialog.Multiselect = $false

if ($initialPath) {{
    if ([System.IO.File]::Exists($initialPath)) {{
        $dialog.InitialDirectory = (
            [System.IO.Path]::GetDirectoryName($initialPath)
        )
        $dialog.FileName = (
            [System.IO.Path]::GetFileName($initialPath)
        )
    }}
    elseif ([System.IO.Directory]::Exists($initialPath)) {{
        $dialog.InitialDirectory = $initialPath
    }}
}}

$result = $dialog.ShowDialog()

if ($result -eq [System.Windows.Forms.DialogResult]::OK) {{
    Write-Output $dialog.FileName
}}
"""

    @staticmethod
    def _encode_powershell_string(
        value: str,
    ) -> str:
        """
        Codifica uma string em Base64 para transporte seguro
        dentro do script PowerShell.
        """

        return base64.b64encode(
            value.encode("utf-8"),
        ).decode("ascii")

    @staticmethod
    def _run_windows_dialog(
        script: str,
    ) -> str | None:
        """
        Executa o seletor nativo do Windows através do PowerShell.
        """

        if os.name != "nt":
            raise RuntimeError(
                "O seletor nativo de arquivos e pastas está "
                "disponível somente no Windows."
            )

        encoded_command = base64.b64encode(
            script.encode("utf-16le"),
        ).decode("ascii")

        completed_process = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-STA",
                "-EncodedCommand",
                encoded_command,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

        if completed_process.returncode != 0:
            error = (
                completed_process.stderr.strip()
                or "Não foi possível abrir o seletor do Windows."
            )

            raise RuntimeError(error)

        selected_path = (
            completed_process.stdout.strip()
        )

        if not selected_path:
            return None

        return selected_path

    def _get_settings_path(
        self,
    ) -> Path:
        """
        Obtém o caminho físico do settings.json.
        """

        return (
            self._configuration_loader.config_path
            / "settings.json"
        )

    @staticmethod
    def _read_raw_configuration(
        settings_path: Path,
    ) -> dict[str, Any]:
        """
        Carrega o JSON completo preservando propriedades que não
        pertencem à configuração editável.
        """

        if not settings_path.exists():
            raise FileNotFoundError(
                "Arquivo de configuração não encontrado: "
                f"{settings_path}"
            )

        with settings_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if not isinstance(
            data,
            dict,
        ):
            raise ValueError(
                "O arquivo settings.json deve conter "
                "um objeto JSON."
            )

        return data

    @staticmethod
    def _write_raw_configuration(
        settings_path: Path,
        data: dict[str, Any],
    ) -> None:
        """
        Grava a configuração de forma atômica.
        """

        settings_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_descriptor, temporary_name = (
            tempfile.mkstemp(
                prefix="settings_",
                suffix=".json",
                dir=settings_path.parent,
                text=True,
            )
        )

        temporary_path = Path(
            temporary_name,
        )

        try:
            with os.fdopen(
                file_descriptor,
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=4,
                )

                file.write("\n")

            os.replace(
                temporary_path,
                settings_path,
            )

        except Exception:
            temporary_path.unlink(
                missing_ok=True,
            )

            raise

    @staticmethod
    def _to_response(
        settings: AppSettings,
    ) -> ConfigurationResponse:
        """
        Converte AppSettings para o contrato público da API.
        """

        return ConfigurationResponse(
            application_name=(
                settings.application_name
            ),
            version=settings.version,
            log_level=settings.log_level,
            base_path=str(
                settings.base_path,
            ),
            installer_path=str(
                settings.installer_path,
            ),
            publish_path=str(
                settings.publish_path,
            ),
            storage=settings.storage,
            build_tools=settings.build_tools,
            setup=settings.setup,
            logging=settings.logging,
        )