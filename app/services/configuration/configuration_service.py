"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : configuration_service.py
Descrição : Responsável por ler e atualizar as configurações
             operacionais do OuroBuild.
--------------------------------------------------------------------
"""

import base64
import os
import subprocess

import httpx

from app.abstractions.application_configuration_repository import (
    ApplicationConfigurationRepository,
)

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
        configuration_repository: ApplicationConfigurationRepository,
    ) -> None:
        if configuration_loader is None:
            raise ValueError(
                "ConfigurationLoader não foi informado."
            )

        if configuration_repository is None:
            raise ValueError(
                "ApplicationConfigurationRepository não foi informado."
            )

        self._configuration_loader = (
            configuration_loader
        )

        self._configuration_repository = (
            configuration_repository
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
        Atualiza as configurações editáveis no SQL Server.

        As configurações de banco de dados e segurança existentes
        são preservadas e não são expostas pela API.
        """

        current_settings = (
            self._configuration_loader.load_settings()
        )

        updated_settings = (
            current_settings.model_copy(
                update={
                    "application_name": (
                        request.application_name.strip()
                    ),
                    "version": (
                        request.version.strip()
                    ),
                    "log_level": (
                        request.log_level.strip().upper()
                    ),
                    "base_path": request.base_path,
                    "installer_path": request.installer_path,
                    "publish_path": request.publish_path,

                    #
                    # Integrações
                    #

                    "ourodeploy_sql_api_url": (
                        request.ourodeploy_sql_api_url.strip()
                    ),

                    #
                    # Armazenamento
                    #

                    "storage": (
                        current_settings.storage.model_copy(
                            update={
                                "workspace_path": (
                                    request.storage.workspace_path
                                ),
                            }
                        )
                    ),

                    #
                    # Ferramentas
                    #

                    "build_tools": (
                        current_settings.build_tools.model_copy(
                            update={
                                "msbuild_path": (
                                    request.build_tools.msbuild_path
                                ),
                                "advanced_installer_path": (
                                    request.build_tools.advanced_installer_path
                                ),
                                "robocopy_path": (
                                    request.build_tools.robocopy_path
                                ),
                                "tf_path": (
                                    request.build_tools.tf_path
                                ),
                            }
                        )
                    ),

                    #
                    # Setup
                    #

                    "setup": (
                        current_settings.setup.model_copy(
                            update={
                                "engine": request.setup.engine,
                                "output_root": (
                                    request.setup.output_root
                                ),
                                "aip_root": (
                                    request.setup.aip_root
                                ),
                                "network_root_path": (
                                    request.setup.network_root_path
                                ),
                                "excluirpastawork": (
                                    request.setup.excluirpastawork
                                ),
                            }
                        )
                    ),

                    #
                    # Logging
                    #

                    "logging": (
                        current_settings.logging.model_copy(
                            update={
                                "enabled": (
                                    request.logging.enabled
                                ),
                                "path": request.logging.path,
                                "level": (
                                    request.logging.level.upper()
                                ),
                            }
                        )
                    ),
                }
            )
        )

        saved_settings = (
            self._configuration_repository.save(
                updated_settings,
            )
        )

        return self._to_response(
            settings=saved_settings,
        )

    def get_ourodeploy_sql_status(
        self,
    ) -> dict[str, object]:
        """
        Verifica o estado da API OuroDeploy SQL.

        A URL configurada representa a URL base da API.
        O health check é realizado através de:

            {base_url}/health

        Returns:
            Dicionário contendo:

            configured:
                Indica se a URL foi configurada.

            online:
                Indica se a API respondeu com sucesso.

            url:
                URL base configurada.

            message:
                Mensagem amigável para apresentação na interface.
        """

        settings = (
            self._configuration_loader.load_settings()
        )

        base_url = (
            settings.ourodeploy_sql_api_url.strip()
        )

        if not base_url:
            return {
                "configured": False,
                "online": False,
                "url": "",
                "message": (
                    "API OuroDeploy SQL não configurada"
                ),
            }

        base_url = base_url.rstrip("/")

        health_url = (
            f"{base_url}/health"
        )

        try:
            response = httpx.get(
                health_url,
                timeout=3.0,
                follow_redirects=True,
            )

            if 200 <= response.status_code < 300:
                return {
                    "configured": True,
                    "online": True,
                    "url": base_url,
                    "message": (
                        "OuroDeploy SQL online"
                    ),
                }

            return {
                "configured": True,
                "online": False,
                "url": base_url,
                "message": (
                    "OuroDeploy SQL offline"
                ),
            }

        except Exception:
            return {
                "configured": True,
                "online": False,
                "url": base_url,
                "message": (
                    "OuroDeploy SQL offline"
                ),
            }

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

            ourodeploy_sql_api_url=(
                settings.ourodeploy_sql_api_url
            ),

            logging=settings.logging,
        )