"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_logger.py
Descrição : Logger utilizado pela Pipeline.
--------------------------------------------------------------------
"""

import inspect
from datetime import datetime
from pathlib import Path

from app.models.configuration.logging_settings import (
    LoggingSettings,
)


class PipelineLogger:
    """
    Logger da Pipeline.

    As configurações são fornecidas pelo Bootstrap através de
    LoggingSettings.

    Exemplo:

        PipelineLogger.info(
            "Pipeline iniciada"
        )

    Será gerado um arquivo como:

        Pipeline_debug.txt
    """

    DEFAULT_SETTINGS = LoggingSettings()

    _settings = DEFAULT_SETTINGS

    LEVELS = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
    }

    @classmethod
    def configure(
        cls,
        settings: LoggingSettings,
    ) -> None:
        """
        Configura o logger com as definições da aplicação.
        """

        if settings is None:
            raise ValueError(
                "As configurações do logger são obrigatórias."
            )

        cls._settings = settings

    @classmethod
    def _is_enabled(
        cls,
    ) -> bool:
        """
        Verifica se o logger está habilitado.
        """

        return cls._settings.enabled

    @classmethod
    def _get_log_level(
        cls,
    ) -> str:
        """
        Retorna o nível configurado para o logger.
        """

        level = (
            cls._settings.level
            .strip()
            .upper()
        )

        if level not in cls.LEVELS:
            return "INFO"

        return level

    @classmethod
    def _get_log_path(
        cls,
    ) -> Path:
        """
        Retorna o diretório dos arquivos de log.
        """

        return cls._settings.path

    @classmethod
    def _get_calling_class_name(
        cls,
    ) -> str:
        """
        Obtém o nome da classe que chamou o logger.
        """

        frame = inspect.currentframe()

        try:
            if frame is None:
                return "Pipeline"

            frame = frame.f_back

            while frame is not None:
                local_self = frame.f_locals.get(
                    "self"
                )

                if local_self is not None:
                    return (
                        local_self
                        .__class__
                        .__name__
                    )

                local_cls = frame.f_locals.get(
                    "cls"
                )

                if isinstance(
                    local_cls,
                    type,
                ):
                    return local_cls.__name__

                frame = frame.f_back

        finally:
            del frame

        return "Pipeline"

    @classmethod
    def _get_calling_method_name(
        cls,
    ) -> str:
        """
        Obtém o nome do método que chamou o logger.
        """

        frame = inspect.currentframe()

        try:
            if frame is None:
                return "unknown"

            frame = frame.f_back

            while frame is not None:
                local_self = frame.f_locals.get(
                    "self"
                )

                local_cls = frame.f_locals.get(
                    "cls"
                )

                if (
                    local_self is not None
                    or isinstance(
                        local_cls,
                        type,
                    )
                ):
                    return frame.f_code.co_name

                frame = frame.f_back

        finally:
            del frame

        return "unknown"

    @classmethod
    def _get_log_file(
        cls,
    ) -> Path:
        """
        Monta o caminho do arquivo de log.
        """

        class_name = (
            cls._get_calling_class_name()
        )

        log_path = cls._get_log_path()

        return (
            log_path
            / f"{class_name}_debug.txt"
        )

    @classmethod
    def _should_log(
        cls,
        level: str,
    ) -> bool:
        """
        Verifica se o nível informado deve ser registrado.
        """

        if not cls._is_enabled():
            return False

        configured_level = (
            cls._get_log_level()
        )

        return (
            cls.LEVELS[level]
            >= cls.LEVELS[configured_level]
        )

    @classmethod
    def write(
        cls,
        message: str,
        level: str = "INFO",
    ) -> None:
        """
        Escreve uma mensagem no arquivo de log.
        """

        level = level.upper()

        if level not in cls.LEVELS:
            level = "INFO"

        if not cls._should_log(
            level
        ):
            return

        log_file = cls._get_log_file()

        log_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        class_name = (
            cls._get_calling_class_name()
        )

        method_name = (
            cls._get_calling_method_name()
        )

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        log_message = (
            f"{timestamp} | "
            f"{level:<7} | "
            f"{class_name}.{method_name} | "
            f"{message}"
        )

        with log_file.open(
            mode="a",
            encoding="utf-8",
        ) as log:
            log.write(
                log_message
            )

            log.write(
                "\n"
            )

    @classmethod
    def debug(
        cls,
        message: str,
    ) -> None:
        """
        Registra uma informação de debug.
        """

        cls.write(
            message,
            "DEBUG",
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
            message,
            "INFO",
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
            message,
            "WARNING",
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
            message,
            "ERROR",
        )

    @classmethod
    def clear(
        cls,
    ) -> None:
        """
        Limpa o arquivo de log da classe chamadora.
        """

        if not cls._is_enabled():
            return

        log_file = cls._get_log_file()

        log_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        log_file.write_text(
            "",
            encoding="utf-8",
        )

    @classmethod
    def separator(
        cls,
    ) -> None:
        """
        Escreve uma linha separadora.
        """

        cls.write(
            "=" * 80,
            "INFO",
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
            "",
            "INFO",
        )

        cls.separator()

        cls.write(
            title,
            "INFO",
        )

        cls.separator()