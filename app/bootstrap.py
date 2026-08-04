"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : bootstrap.py
Descrição : Responsável por inicializar a aplicação e criar as
             dependências da aplicação.
--------------------------------------------------------------------
"""

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

        #
        # Services
        #

        self.process_service = DefaultProcessService()

        #
        # Factories
        #

        self.pipeline_factory = DefaultPipelineFactory(
            process_service=self.process_service,
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
        #
        # Use Cases
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
            )
        )
        self.execute_publish_use_case = (
            ExecutePublishUseCase(
                publish_context_factory=self.publish_context_factory,
                pipeline_factory=self.pipeline_factory,
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
        return app