"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : windows_visual_studio_locator.py
Descrição : Localiza o executável devenv.com do Visual Studio
             em ambiente Windows.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.services.setup.visual_studio_locator import (
    VisualStudioLocator,
)


class WindowsVisualStudioLocator(
    VisualStudioLocator,
):
    """
    Localiza o executável do Visual Studio no Windows.
    """

    _DEFAULT_PATHS = (
        Path(
            r"C:\Program Files\Microsoft Visual Studio"
        ),
        Path(
            r"C:\Program Files (x86)\Microsoft Visual Studio"
        ),
    )

    def locate(self) -> Path:
        """
        Localiza o executável devenv.com.

        Procura nas instalações padrão do Visual Studio.
        """

        for root in self._DEFAULT_PATHS:

            if not root.exists():
                continue

            candidates = root.rglob(
                "Common7/IDE/devenv.com"
            )

            for candidate in candidates:

                if candidate.is_file():
                    return candidate

        raise FileNotFoundError(
            "Executável 'devenv.com' do Visual Studio "
            "não foi encontrado."
        )