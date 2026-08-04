"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : msbuild_locator.py
Descrição : Responsável por localizar o MSBuild.exe.
--------------------------------------------------------------------
"""

import subprocess

from pathlib import Path

from app.models.toolchain.toolchain_settings import (
    ToolchainSettings,
)


class MSBuildLocator:
    """
    Responsável por localizar o MSBuild.exe.
    """

    def __init__(
        self,
        toolchain: ToolchainSettings,
    ) -> None:

        self.__toolchain = toolchain

        self.__cached_path: Path | None = None

    def get_msbuild_path(
        self,
    ) -> Path:
        """
        Retorna o caminho do MSBuild.exe.
        """

        #
        # Cache
        #

        if self.__cached_path is not None:

            return self.__cached_path

        #
        # Caminho informado manualmente
        #

        configured_path = (
            self.__toolchain.msbuild.path
        )

        if configured_path:

            path = Path(
                configured_path,
            )

            if path.exists():

                self.__cached_path = path

                return path

        #
        # Descoberta automática
        #

        if not self.__toolchain.msbuild.auto_detect:

            raise FileNotFoundError(
                "MSBuild.exe não configurado."
            )

        vswhere = Path(
            self.__toolchain.vswhere.path,
        )

        if not vswhere.exists():

            raise FileNotFoundError(
                f"VSWhere não encontrado: {vswhere}"
            )

        result = subprocess.run(

            [

                str(vswhere),

                "-latest",

                "-products",

                "*",

                "-requires",

                "Microsoft.Component.MSBuild",

                "-find",

                r"MSBuild\**\Bin\MSBuild.exe",

            ],

            capture_output=True,

            text=True,

            check=False,
        )

        executable = result.stdout.strip()

        if not executable:

            raise FileNotFoundError(
                "MSBuild.exe não localizado."
            )

        self.__cached_path = Path(
            executable,
        )

        return self.__cached_path