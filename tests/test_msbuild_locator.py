"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_msbuild_locator.py
Descrição : Teste do MSBuildLocator.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.core.configuration.toolchain_loader import (
    ToolchainLoader,
)
from app.services.msbuild_locator import (
    MSBuildLocator,
)


def main():

    configuration_path = Path("config")

    toolchain = ToolchainLoader(
        configuration_path=configuration_path,
    ).load()

    locator = MSBuildLocator(
        toolchain=toolchain,
    )

    path = locator.get_msbuild_path()

   

if __name__ == "__main__":
    main()