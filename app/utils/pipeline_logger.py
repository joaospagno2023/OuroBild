"""
Logger utilizado para depuração da Pipeline.
"""

from pathlib import Path


class PipelineLogger:
    """
    Logger simples para registrar informações da Pipeline
    em arquivo.
    """

    LOG_FILE = Path(
        r"C:\Custom\ourobuild\app\logs\pipeline_debug.txt"
    )

    @classmethod
    def clear(
        cls,
    ) -> None:
        """
        Limpa o arquivo de log.
        """

        cls.LOG_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        cls.LOG_FILE.write_text(
            "",
            encoding="utf-8",
        )

    @classmethod
    def write(
        cls,
        message: str,
    ) -> None:
        """
        Escreve uma mensagem no arquivo de log.
        """

        cls.LOG_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            cls.LOG_FILE,
            "a",
            encoding="utf-8",
        ) as log:

            log.write(
                message
            )

            log.write(
                "\n"
            )

    @classmethod
    def info(
        cls,
        message: str,
    ) -> None:
        """
        Registra uma informação.
        """

        cls.write(
            message
        )

    @classmethod
    def warning(
        cls,
        message: str,
    ) -> None:
        """
        Registra um warning.
        """

        cls.write(
            f"[WARNING] {message}"
        )

    @classmethod
    def error(
        cls,
        message: str,
    ) -> None:
        """
        Registra um erro.
        """

        cls.write(
            f"[ERROR] {message}"
        )

    @classmethod
    def separator(
        cls,
    ) -> None:
        """
        Escreve uma linha separadora.
        """

        cls.write(
            "=" * 80
        )

    @classmethod
    def header(
        cls,
        title: str,
    ) -> None:
        """
        Escreve um cabeçalho no log.
        """

        cls.write(
            ""
        )

        cls.separator()

        cls.write(
            title
        )

        cls.separator()