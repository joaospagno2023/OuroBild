"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : bootstrap.py
Descrição : Responsável por inicializar a aplicação e criar as
             dependências da aplicação.
--------------------------------------------------------------------
"""
import inspect

from pathlib import Path

from fastapi import FastAPI

# Routers
from app.api.routers.build_router import (
    router as build_router,
)
from app.api.routers.project_router import (
    router as project_router,
)

# Core
from app.core.configuration.configuration_loader import (
    ConfigurationLoader,
)

# Factories
from app.factories.build_context_factory import (
    BuildContextFactory,
)
from app.factories.default_pipeline_factory import (
    DefaultPipelineFactory,
)

# Repositories
from app.pipeline.runner.pipeline_runner import PipelineRunner
from app.repositories.json_environment_repository import (
    JsonEnvironmentRepository,
)
from app.repositories.json_project_repository import (
    JsonProjectRepository,
)

# Services
from app.services.default_process_service import (
    DefaultProcessService,
)

# Use Cases
from app.use_cases.execute_build_use_case import (
    ExecuteBuildUseCase,
)
from app.use_cases.execute_pipeline_use_case import (
    ExecutePipelineUseCase,
)
from app.use_cases.get_projects_use_case import (
    GetProjectsUseCase,
)

from app.api.exception_handlers import (
    register_exception_handlers,
)

from app.factories.publish_context_factory import (
    PublishContextFactory,
)

from app.use_cases.execute_publish_use_case import (
    ExecutePublishUseCase,
)

from app.api.routers.publish_router import (
    router as publish_router,
)

from app.core.configuration.toolchain_loader import (
    ToolchainLoader,
)

from app.services.msbuild_locator import (
    MSBuildLocator,
)
from app.api.routers.analyze_router import (
    router as analyze_router,
)

from app.analyzers.build_analyzer import (
    BuildAnalyzer,
)

from app.analyzers.framework_analyzer import (
    FrameworkAnalyzer,
)

from app.analyzers.project_analyzer import (
    ProjectAnalyzer,
)

from app.factories.analysis_context_factory import (
    AnalysisContextFactory,
)

from app.readers.project_reader import (
    ProjectReader,
)

from app.use_cases.execute_analyze_use_case import (
    ExecuteAnalyzeUseCase,
)

from app.validators.project_validator import (
    ProjectValidator,
)

# Workspace
from app.workspace.workspace_resolver import (
    WorkspaceResolver,
)

# Services
from app.services.default_process_service import (
    DefaultProcessService,
)

from app.repositories.json_project_metadata_repository import (
    JsonProjectMetadataRepository,
)
from app.services.hash_service import (
    HashService,
)

from app.services.project_metadata_service import (
    ProjectMetadataService,
)

from app.services.workspace.solution_locator_service import (
    SolutionLocatorService,
)
from app.pipeline.runner.pipeline_runner import (
    PipelineRunner,
)
from app.repositories.json_pipeline_execution_repository import (
    JsonPipelineExecutionRepository,
)

class Bootstrap:
    """
    Responsável por criar e inicializar a aplicação.
    """

    def __init__(
        self,
    ) -> None:

        configuration_path = Path("config")

        #
        # Configurações
        #

        self.configuration_loader = ConfigurationLoader(
            config_path=configuration_path,
        )

        self.settings = (
            self.configuration_loader.load_settings()
        )

        #
        # Toolchain
        #

        self.toolchain = (
            ToolchainLoader(
                configuration_path=configuration_path,
            ).load()
        )

        self.msbuild_locator = (
            MSBuildLocator(
                toolchain=self.toolchain,
            )
        )
        #
        # Repositórios
        #

        self.project_repository = JsonProjectRepository(
            configuration_path=configuration_path,
            settings=self.settings,
        )

        self.environment_repository = (
            JsonEnvironmentRepository(
                configuration_path=configuration_path,
            )
        )

        self.project_metadata_repository = (
            JsonProjectMetadataRepository(
                metadata_path=Path("metadata"),
            )
        )
#
        # Workspace
        #

        self.workspace_resolver = (
            WorkspaceResolver(
                project_repository=self.project_repository,
                environment_repository=self.environment_repository,
            )
        )

        #
        # Services
        #

        self.process_service = (
            DefaultProcessService()
        )

        self.hash_service = (
            HashService() 
        )

        self.project_metadata_service = (
            ProjectMetadataService(
                repository=self.project_metadata_repository,
                hash_service=self.hash_service,
            )
        )
        #
        # Repositório de execuções
        #

        self.pipeline_execution_repository = (
            JsonPipelineExecutionRepository(
                settings=self.settings,
            )
        )
       

        #
        # Pipeline Runner
        #
        print()
        print("=" * 80)
        print("DEBUG PIPELINE RUNNER")
        print("=" * 80)
        print("ARQUIVO:", inspect.getfile(PipelineRunner))
        print("CLASSE:", PipelineRunner)
        print("INIT:", inspect.signature(PipelineRunner.__init__))
        print("=" * 80) 
        
        self.pipeline_runner = (
            PipelineRunner(
                repository=self.pipeline_execution_repository,
            )
        )

            

        self.project_metadata_service = (
            ProjectMetadataService(
                repository=self.project_metadata_repository,
                hash_service=self.hash_service,
            )
        )

       

        #
        # Factories
        #

        self.pipeline_factory = DefaultPipelineFactory(
            process_service=self.process_service,
            msbuild_locator=self.msbuild_locator,
        )

        self.build_context_factory = (
            BuildContextFactory(
                project_repository=self.project_repository,
                environment_repository=self.environment_repository,
            )
        )
        self.publish_context_factory = (
            PublishContextFactory(
                project_repository=self.project_repository,
                environment_repository=self.environment_repository,
            )
        )
        self.analysis_context_factory = (
            AnalysisContextFactory()
        )

        #
        # Analysis
        #
        self.project_reader = (
            ProjectReader()
        )
    
        self.project_analyzer = (
            ProjectAnalyzer()
        )
    
        self.framework_analyzer = (
            FrameworkAnalyzer()
        )
    
        self.build_analyzer = (
            BuildAnalyzer()
        )
    
        self.project_validator = (
            ProjectValidator()
        )
        #
        # DEMAIS ARQUIVOS
        #
    

        self.solution_locator_service = (
            SolutionLocatorService()
        )

        
        #
        # Use Cases Sempre  deve ir por ultio
        #

        self.get_projects_use_case = (
            GetProjectsUseCase(
                repository=self.project_repository,
            )
        )

        self.execute_pipeline_use_case = (
            ExecutePipelineUseCase(
                project_repository=self.project_repository,
                pipeline_factory=self.pipeline_factory,
            )
        )
        self.execute_build_use_case = (
            ExecuteBuildUseCase(
                build_context_factory=self.build_context_factory,
                pipeline_factory=self.pipeline_factory,
                solution_locator=self.solution_locator_service,
                pipeline_runner=self.pipeline_runner,
                publish_context_factory=self.publish_context_factory,
            )
        )
        self.execute_publish_use_case = (
            ExecutePublishUseCase(
                publish_context_factory=self.publish_context_factory,
                pipeline_factory=self.pipeline_factory,
                solution_locator=self.solution_locator_service,
                pipeline_runner=self.pipeline_runner,
            )
        )
        self.execute_analyze_use_case = (
            ExecuteAnalyzeUseCase(
                project_metadata_service=self.project_metadata_service,
                workspace_resolver=self.workspace_resolver,
                analysis_context_factory=self.analysis_context_factory,
                project_reader=self.project_reader,
                project_analyzer=self.project_analyzer,
                framework_analyzer=self.framework_analyzer,
                build_analyzer=self.build_analyzer,
                project_validator=self.project_validator,
            )
        )

        


    def create_app(
        self,
    ) -> FastAPI:
        """
        Cria e configura a aplicação.
        """

        app = FastAPI(
            title="OuroBuild",
            description="Sistema interno de automação de builds da OuroWeb",
            version=self.settings.version,
        )

        #
        # Tratamento global de exceções
        #

        register_exception_handlers(
            app,
        )
        
        @app.get("/")
        def root():
            return {
                "application": self.settings.application_name,
                "version": self.settings.version,
                "status": "running",
            }

        @app.get("/health")
        def health():
            return {
                "status": "healthy",
            }

        app.state.bootstrap = self

        app.include_router(
            project_router,
        )

        app.include_router(
            build_router,
        )
        app.include_router(
            publish_router,
        )
        app.include_router(
            analyze_router,
        )
        return app