"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_executor_factory_impl.py
Descrição : Implementação da Factory responsável por fornecer
            o executor de Build adequado para cada engine.
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

from app.services.process.process_executor_service import (
    ProcessExecutorService,
)


class BuildExecutorFactoryImpl(
    BuildExecutorFactory,
):
    """
    Implementação padrão da Factory de Build.

    Responsável por selecionar o executor adequado
    conforme a engine de compilação do projeto.
    """

    def __init__(
        self,
        process_executor_service: ProcessExecutorService,
    ) -> None:
        """
        Inicializa a Factory.
        """

        self.__process = (
            process_executor_service
        )

    def create(
        self,
        engine: CompilationEngine,
    ) -> BuildExecutorService:
        """
        Cria o executor correspondente à engine.
        """

        match engine:

            case CompilationEngine.DOTNET:

                return DotnetBuildExecutorService(
                    process_executor_service=(
                        self.__process
                    ),
                )

            case CompilationEngine.MSBUILD:

                raise NotImplementedError(
                    "Executor MSBuild ainda não "
                    "foi integrado à Factory."
                )

            case _:

                raise ValueError(
                    f"Engine não suportada: {engine}"
                )