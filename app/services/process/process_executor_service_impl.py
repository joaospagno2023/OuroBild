"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_executor_factory_impl.py
Descrição : Implementação da BuildExecutorFactory.
--------------------------------------------------------------------
"""

from app.models.build.compilation_engine import (
    CompilationEngine,
)
from app.services.build.build_executor_factory import (
    BuildExecutorFactory,
)
from app.services.build.build_executor_service import (
    BuildExecutorService,
)
from app.services.build.dotnet_build_executor_service import (
    DotnetBuildExecutorService,
)
from app.services.build.msbuild_build_executor_service import (
    MSBuildExecutorService,
)
from app.services.process.process_executor_service import (
    ProcessExecutorService,
)


class BuildExecutorFactoryImpl(
    BuildExecutorFactory,
):
    """
    Implementação padrão da Factory.
    """

    def __init__(
        self,
        process_executor_service: ProcessExecutorService,
    ) -> None:

        self.__process = process_executor_service

    def create(
        self,
        engine: CompilationEngine,
    ) -> BuildExecutorService:

        match engine:

            case CompilationEngine.DOTNET:

                return DotnetBuildExecutorService(
                    process_executor_service=self.__process,
                )

            case CompilationEngine.MSBUILD:

                return MSBuildExecutorService(
                    process_executor_service=self.__process,
                )

            case _:

                raise ValueError(
                    f"Engine não suportada: {engine}"
                )