"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : base_validator.py
Descrição : Classe base para os Validators.
--------------------------------------------------------------------
"""

from app.models.analyzers.diagnostic import (
    Diagnostic,
)
from app.models.analyzers.severity import (
    Severity,
)


class BaseValidator:
    """
    Classe base para todos os Validators.
    """

    def create_error(
        self,
        code: str,
        message: str,
    ) -> Diagnostic:
        """
        Cria um diagnóstico de erro.
        """

        return Diagnostic(

            code=code,

            severity=Severity.ERROR,

            message=message,

            source=self.__class__.__name__,
        )

    def create_warning(
        self,
        code: str,
        message: str,
    ) -> Diagnostic:
        """
        Cria um diagnóstico de aviso.
        """

        return Diagnostic(

            code=code,

            severity=Severity.WARNING,

            message=message,

            source=self.__class__.__name__,
        )

    def create_info(
        self,
        code: str,
        message: str,
    ) -> Diagnostic:
        """
        Cria um diagnóstico informativo.
        """

        return Diagnostic(

            code=code,

            severity=Severity.INFO,

            message=message,

            source=self.__class__.__name__,
        )