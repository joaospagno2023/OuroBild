"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_logger.py
Descrição : Logger utilizado pela Pipeline.
--------------------------------------------------------------------
"""

import inspect
import re
from contextvars import ContextVar
from datetime import datetime
from pathlib import Path

from app.abstractions.pipeline_execution_log_repository import (
    PipelineExecutionLogRepository,
)
from app.models.configuration.logging_settings import (
    LoggingSettings,
)
from app.models.logging.pipeline_execution_log import (
    PipelineExecutionLog,
)


class PipelineLogger:
    """
    Logger da Pipeline.

    As configurações são fornecidas pelo Bootstrap através de
    LoggingSettings.

    Os logs da execução podem ser persistidos no repositório
    de PipelineExecutionLogRepository.

    Exemplo:

        PipelineLogger.info(
            "Pipeline iniciada"
        )

    Será gerado um arquivo como:

        Pipeline_debug.txt
    """

    DEFAULT_SETTINGS = LoggingSettings()

    _settings = DEFAULT_SETTINGS

    _repository: PipelineExecutionLogRepository | None = None

    _execution_id: ContextVar[str | None] = ContextVar(
        "ourobuild_pipeline_execution_id",
        default=None,
    )

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
        repository: PipelineExecutionLogRepository | None = None,
    ) -> None:
        """
        Configura o logger com as definições da aplicação.

        O repositório é opcional para preservar a possibilidade
        de utilizar o logger sem persistência em banco.
        """

        if settings is None:
            raise ValueError(
                "As configurações do logger são obrigatórias."
            )

        cls._settings = settings
        cls._repository = repository

    @classmethod
    def set_execution_id(
        cls,
        execution_id: str,
    ) -> None:
        """
        Define a execução atual para os logs da Pipeline.
        """

        if not execution_id:
            raise ValueError(
                "O execution_id é obrigatório."
            )

        cls._execution_id.set(execution_id)

    @classmethod
    def clear_execution_id(
        cls,
    ) -> None:
        """
        Remove o contexto da execução atual.
        """

        cls._execution_id.set(None)

    @classmethod
    def _get_execution_id(
        cls,
    ) -> str | None:
        """
        Retorna o identificador da execução atual.
        """

        return cls._execution_id.get()

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
    def _get_execution_log_file(
        cls,
    ) -> Path | None:
        """
        Retorna o arquivo de log associado à execução atual.
        """

        execution_id = cls._get_execution_id()

        if not execution_id:
            return None

        if re.fullmatch(
            r"[A-Fa-f0-9]+",
            execution_id,
        ) is None:
            return None

        return (
            cls._get_log_path()
            / "executions"
            / execution_id
            / "pipeline.log"
        )

    @classmethod
    def get_execution_log(
        cls,
        execution_id: str,
    ) -> str | None:
        """
        Retorna os logs persistidos localmente de uma execução.
        """

        if re.fullmatch(
            r"[A-Fa-f0-9]+",
            execution_id or "",
        ) is None:
            return None

        log_file = (
            cls._get_log_path()
            / "executions"
            / execution_id
            / "pipeline.log"
        )

        if not log_file.is_file():
            return None

        try:
            return log_file.read_text(
                encoding="utf-8",
            )
        except OSError:
            return None

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
    def _persist_execution_log(
        cls,
        execution_id: str | None,
        timestamp: datetime,
        level: str,
        source: str,
        message: str,
    ) -> None:
        """
        Persiste o log da execução no repositório configurado.

        Falhas de persistência não interrompem a Pipeline. O
        arquivo local continua sendo a proteção técnica para
        problemas de disponibilidade do banco.
        """

        if (
            execution_id is None
            or cls._repository is None
        ):
            return

        log = PipelineExecutionLog(
            execution_id=execution_id,
            timestamp=timestamp,
            level=level,
            source=source,
            message=message,
            details=None,
        )

        try:
            cls._repository.save(log)
        except Exception:
            return

    @classmethod
    def write(
        cls,
        message: str,
        level: str = "INFO",
    ) -> None:
        """
        Escreve uma mensagem no arquivo de log e, quando houver
        uma execução ativa, persiste também no banco de dados.
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

        timestamp = datetime.now()

        timestamp_text = timestamp.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        log_message = (
            f"{timestamp_text} | "
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

        execution_log_file = (
            cls._get_execution_log_file()
        )

        if execution_log_file is not None:
            execution_log_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with execution_log_file.open(
                mode="a",
                encoding="utf-8",
            ) as log:
                log.write(
                    log_message
                )

                log.write(
                    "\n"
                )

        execution_id = (
            cls._get_execution_id()
        )

        cls._persist_execution_log(
            execution_id=execution_id,
            timestamp=timestamp,
            level=level,
            source=class_name,
            message=message,
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