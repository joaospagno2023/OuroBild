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
from app.api.routers.project_router import router as project_router

# Core
from app.core.configuration.configuration_loader import ConfigurationLoader

# Factories
from app.factories.default_pipeline_factory import (
    DefaultPipelineFactory,
)

# Repositories
from app.repositories.json_project_repository import (
    JsonProjectRepository,
)

# Services
from app.services.default_process_service import (
    DefaultProcessService,
)

# Use Cases
from app.use_cases.execute_pipeline_use_case import (
    ExecutePipelineUseCase,
)
from app.use_cases.get_projects_use_case import (
    GetProjectsUseCase,
)

from app.repositories.json_environment_repository import (
    JsonEnvironmentRepository,
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
        #
        # Repositories
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

        #
        # Use Cases
        #

        self.get_projects_use_case = GetProjectsUseCase(
            repository=self.project_repository,
        )

        self.execute_pipeline_use_case = (
            ExecutePipelineUseCase(
                project_repository=self.project_repository,
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

        app.include_router(project_router)

        return app