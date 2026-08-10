"""
---------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_runner.py
Descrição: Responsável por executar todas as etapas da Pipeline.
----------------------------------------------------------------------
"""

from datetime import datetime
import inspect

from app.abstractions.pipeline_execution_repository import (
    PipelineExecutionRepository,
)
from app.models.build.build_execution import (
    BuildExecution,
)
from app.models.pipeline.pipeline import (
    Pipeline,
)
from app.models.pipeline.pipeline_context import (
    PipelineContext,
)
from app.models.pipeline.pipeline_result import (
    PipelineResult,
)
from app.models.pipeline.step_status import (
    StepStatus,
)
from app.models.publish.publish_execution import (
    PublishExecution,
)
from app.pipeline.runner.step_executor import (
    StepExecutor,
)
from app.utils.pipeline_logger import (
    PipelineLogger,
)


class PipelineRunner:
    """
    Executa todas as etapas da Pipeline.
    """

    def __init__(
        self,
        repository: PipelineExecutionRepository,
    ) -> None:

        self.__repository = repository

        self.__step_executor = StepExecutor()

    def execute(
        self,
        pipeline: Pipeline,
        context: PipelineContext,
    ) -> PipelineResult:

        result = PipelineResult(
            started_at=datetime.now(),
        )

        PipelineLogger.info(
            "=" * 80,
        )

        PipelineLogger.info(
            "PIPELINE RUNNER - INICIO",
        )

        PipelineLogger.info(
            "=" * 80,
        )

        PipelineLogger.info(
            f"Arquivo........: "
            f"{inspect.getfile(self.__class__)}",
        )

        PipelineLogger.info(
            f"Pipeline.......: "
            f"{pipeline.name}",
        )

        PipelineLogger.info(
            f"Quantidade Steps: "
            f"{len(pipeline.steps)}",
        )

        PipelineLogger.info(
            "=" * 80,
        )

        try:

            for step in pipeline.steps:

                PipelineLogger.info(
                    "",
                )

                PipelineLogger.info(
                    "=" * 80,
                )

                PipelineLogger.info(
                    f"EXECUTANDO STEP: "
                    f"{step.name}",
                )

                PipelineLogger.info(
                    f"STEP CLASS.....: "
                    f"{step.__class__.__name__}",
                )

                PipelineLogger.info(
                    "=" * 80,
                )

                step_result = (
                    self.__step_executor.execute(
                        pipeline=pipeline,
                        step=step,
                        context=context,
                    )
                )

                PipelineLogger.info(
                    "",
                )

                PipelineLogger.info(
                    "=" * 80,
                )

                PipelineLogger.info(
                    "PIPELINE RUNNER - STEP RESULT",
                )

                PipelineLogger.info(
                    "=" * 80,
                )

                PipelineLogger.info(
                    f"Step............: "
                    f"{step_result.name}",
                )

                PipelineLogger.info(
                    f"Status..........: "
                    f"{step_result.status}",
                )

                PipelineLogger.info(
                    f"Analysis........: "
                    f"{type(step_result.analysis)}",
                )

                if step_result.analysis is not None:

                    if hasattr(
                        step_result.analysis,
                        "warnings",
                    ):

                        PipelineLogger.info(
                            f"Warnings........: "
                            f"{len(step_result.analysis.warnings)}",
                        )

                    if hasattr(
                        step_result.analysis,
                        "errors",
                    ):

                        PipelineLogger.info(
                            f"Errors..........: "
                            f"{len(step_result.analysis.errors)}",
                        )

                result.steps.append(
                    step_result,
                )

                analysis = step_result.analysis

                # ---------------------------------------------------------
                # BUILD
                # ---------------------------------------------------------

                if isinstance(
                    analysis,
                    BuildExecution,
                ):

                    PipelineLogger.info(
                        "",
                    )

                    PipelineLogger.info(
                        "=" * 80,
                    )

                    PipelineLogger.info(
                        "BUILD EXECUTION",
                    )

                    PipelineLogger.info(
                        "=" * 80,
                    )

                    PipelineLogger.info(
                        f"Warnings........: "
                        f"{len(analysis.warnings)}",
                    )

                    PipelineLogger.info(
                        f"Errors..........: "
                        f"{len(analysis.errors)}",
                    )

                    result.build = analysis

                    PipelineLogger.info(
                        "BUILD ARMAZENADO EM PipelineResult",
                    )

                    PipelineLogger.info(
                        "=" * 80,
                    )

                # ---------------------------------------------------------
                # PUBLISH
                # ---------------------------------------------------------

                elif isinstance(
                    analysis,
                    PublishExecution,
                ):

                    PipelineLogger.info(
                        "",
                    )

                    PipelineLogger.info(
                        "=" * 80,
                    )

                    PipelineLogger.info(
                        "PUBLISH EXECUTION",
                    )

                    PipelineLogger.info(
                        "=" * 80,
                    )

                    result.publish = analysis

                    PipelineLogger.info(
                        "PUBLISH ARMAZENADO EM PipelineResult",
                    )

                    PipelineLogger.info(
                        "=" * 80,
                    )

                # ---------------------------------------------------------
                # STEP FAILED
                # ---------------------------------------------------------

                if (
                    step_result.status
                    == StepStatus.FAILED
                ):

                    PipelineLogger.info(
                        "",
                    )

                    PipelineLogger.info(
                        "=" * 80,
                    )

                    PipelineLogger.info(
                        "STEP FALHOU",
                    )

                    PipelineLogger.info(
                        "=" * 80,
                    )

                    PipelineLogger.info(
                        f"Step............: "
                        f"{step_result.name}",
                    )

                    PipelineLogger.info(
                        f"Mensagem........: "
                        f"{step_result.message}",
                    )

                    PipelineLogger.info(
                        "PIPELINE SERÁ INTERROMPIDA",
                    )

                    PipelineLogger.info(
                        "PUBLISH NÃO SERÁ EXECUTADO",
                    )

                    PipelineLogger.info(
                        "=" * 80,
                    )

                    result.success = False

                    result.failed_step = (
                        step_result.name
                    )

                    result.message = (
                        step_result.message
                    )

                    break

        finally:

            finished_at = datetime.now()

            result.finished_at = (
                finished_at
            )

            if result.started_at is not None:

                result.elapsed_seconds = (
                    finished_at
                    - result.started_at
                ).total_seconds()

            PipelineLogger.info(
                "",
            )

            PipelineLogger.info(
                "=" * 80,
            )

            PipelineLogger.info(
                "PIPELINE RESULT",
            )

            PipelineLogger.info(
                "=" * 80,
            )

            PipelineLogger.info(
                f"Success.........: "
                f"{result.success}",
            )

            PipelineLogger.info(
                f"Failed Step.....: "
                f"{result.failed_step}",
            )

            PipelineLogger.info(
                f"Elapsed.........: "
                f"{result.elapsed_seconds}",
            )

            if result.build is None:

                PipelineLogger.info(
                    "Build...........: None",
                )

            else:

                PipelineLogger.info(
                    f"Build Warnings..: "
                    f"{len(result.build.warnings)}",
                )

                PipelineLogger.info(
                    f"Build Errors....: "
                    f"{len(result.build.errors)}",
                )

            if result.publish is None:

                PipelineLogger.info(
                    "Publish.........: None",
                )

            else:

                PipelineLogger.info(
                    "Publish.........: Executado",
                )

            PipelineLogger.info(
                f"Steps executadas: "
                f"{len(result.steps)}",
            )

            PipelineLogger.info(
                "=" * 80,
            )

            PipelineLogger.info(
                "SALVANDO EXECUÇÃO",
            )

            PipelineLogger.info(
                "=" * 80,
            )

            self.__repository.save(
                result,
            )

            PipelineLogger.info(
                "EXECUÇÃO SALVA",
            )

            PipelineLogger.info(
                "=" * 80,
            )

        PipelineLogger.info(
            "",
        )

        PipelineLogger.info(
            "=" * 80,
        )

        PipelineLogger.info(
            "PIPELINE RUNNER - FINAL",
        )

        PipelineLogger.info(
            "=" * 80,
        )

        PipelineLogger.info(
            f"PipelineResult...: "
            f"{type(result)}",
        )

        PipelineLogger.info(
            f"Build............: "
            f"{type(result.build)}",
        )

        PipelineLogger.info(
            f"Publish..........: "
            f"{type(result.publish)}",
        )

        PipelineLogger.info(
            f"Steps............: "
            f"{len(result.steps)}",
        )

        PipelineLogger.info(
            "=" * 80,
        )

        return result