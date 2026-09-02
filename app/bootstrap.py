"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : bootstrap.py
DescriÃ§Ã£o : ResponsÃ¡vel por inicializar a aplicaÃ§Ã£o e criar as
             dependÃªncias da aplicaÃ§Ã£o.
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
from app.services.setup.windows_visual_studio_locator import (
    WindowsVisualStudioLocator,
)

from app.services.setup.visual_studio_installer_service import (
    VisualStudioInstallerService,
)

from app.services.setup.advanced_installer_setup_definition_loader import (
    AdvancedInstallerSetupDefinitionLoader,
)

from app.services.setup.setup_factory import (
    DefaultSetupFactory,
)

from app.services.setup.setup_path_resolver import (
    SetupPathResolver,
)

from app.services.setup.visual_studio_setup_definition_loader import (
    VisualStudioSetupDefinitionLoader,
)

from app.services.setup.setup_orchestrator import (
    DefaultSetupOrchestrator,
)
from app.use_cases.execute_setup_use_case import (
    DefaultExecuteSetupUseCase,
)

from app.services.setup.setup_file_change_applier import (
    SetupFileChangeApplier,
)

from app.services.setup.setup_file_synchronizer import (
    SetupFileSynchronizer,
)

from app.services.setup.setup_file_template_provider import (
    SetupFileTemplateProvider,
)

from app.services.setup.setup_project_preparer import (
    SetupProjectPreparer,
)

from app.services.setup.setup_workspace_service import (
    SetupWorkspaceService,
)

from app.services.setup.vdproj_block_parser import (
    VdprojBlockParser,
)

from app.services.setup.vdproj_component_identity_generator import (
    VdprojComponentIdentityGenerator,
)

from app.services.setup.vdproj_file_block_builder import (
    VdprojFileBlockBuilder,
)

from app.services.setup.vdproj_file_block_inserter import (
    VdprojFileBlockInserter,
)

from app.services.setup.vdproj_file_modifier import (
    VdprojFileModifier,
)

from app.services.setup.vdproj_setup_file_loader import (
    VdprojSetupFileLoader,
)
from app.services.setup.temporary_solution_service import (
    TemporarySolutionService,
)
from app.services.setup.disable_out_of_proc_build_service import (
    DisableOutOfProcBuildService,
)

from app.services.setup.advanced_installer_service import (
    AdvancedInstallerService,
)
from app.services.setup.advanced_installer_aip_file_parser import (
    AdvancedInstallerAipFileParser,
)
from app.services.setup.advanced_installer_aip_file_comparator import (
    AdvancedInstallerAipFileComparator,
)
from app.services.setup.advanced_installer_aip_modifier import (
    AdvancedInstallerAipModifier,
)
from app.services.setup.advanced_installer_aip_synchronizer import (
    AdvancedInstallerAipSynchronizer,
)
from app.services.cleanup.build_artifact_cleanup_factory import (
    BuildArtifactCleanupFactory,
)

class Bootstrap:
    """
    ResponsÃ¡vel por criar e inicializar a aplicaÃ§Ã£o.
    """

    def __init__(
        self,
    ) -> None:

        configuration_path = Path("config")

        #
        # ConfiguraÃ§Ãµes
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
        # RepositÃ³rios
        #

        self.project_repository = JsonProjectRepository(
            configuration_path=configuration_path,
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
        # RepositÃ³rio de execuÃ§Ãµes
        #

        self.pipeline_execution_repository = (
            JsonPipelineExecutionRepository(
                settings=self.settings,
            )
        )

        #
        # Pipeline Runner
        #

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
            project_metadata_service=(
                self.project_metadata_service
            ),
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

        self.setup_path_resolver = (
            SetupPathResolver()
        )

        self.visual_studio_setup_definition_loader = (
            VisualStudioSetupDefinitionLoader()
        )

        #
        # Setup
        #

        self.visual_studio_locator = (
            WindowsVisualStudioLocator()
        )

        self.disable_out_of_proc_build_service = (
            DisableOutOfProcBuildService(
                process_service=self.process_service,
            )
        )

        self.visual_studio_installer_service = (
            VisualStudioInstallerService(
                process_service=self.process_service,
                visual_studio_locator=(
                    self.visual_studio_locator
                ),
                disable_out_of_proc_build_service=(
                    self.disable_out_of_proc_build_service
                ),
            )
        )

        self.cleanup_factory = BuildArtifactCleanupFactory()

        self.advanced_installer_aip_file_parser = (
            AdvancedInstallerAipFileParser()
        )

        self.advanced_installer_aip_file_comparator = (
            AdvancedInstallerAipFileComparator()
        )

        self.advanced_installer_aip_modifier = (
            AdvancedInstallerAipModifier()
        )

        self.advanced_installer_aip_synchronizer = (
            AdvancedInstallerAipSynchronizer(
                parser=(
                    self.advanced_installer_aip_file_parser
                ),
                comparator=(
                    self.advanced_installer_aip_file_comparator
                ),
                modifier=(
                    self.advanced_installer_aip_modifier
                ),
            )
        )

        self.advanced_installer_service = (
            AdvancedInstallerService(
                process_service=self.process_service,
                advanced_installer_path=(
                    self.settings.build_tools.advanced_installer_path
                ),
                cleanup_factory=self.cleanup_factory,
                aip_synchronizer=(
                    self.advanced_installer_aip_synchronizer
                ),
            )
        )

        self.setup_factory = (
            DefaultSetupFactory(
                visual_studio_installer=(
                    self.visual_studio_installer_service
                ),
                advanced_installer=(
                    self.advanced_installer_service
                ),
            )
        )

        self.advanced_installer_setup_definition_loader = (
            AdvancedInstallerSetupDefinitionLoader()
        )

        #
        # PreparaÃ§Ã£o do projeto Visual Studio Setup
        #

        self.vdproj_block_parser = (
            VdprojBlockParser()
        )

        self.vdproj_setup_file_loader = (
            VdprojSetupFileLoader(
                parser=self.vdproj_block_parser,
            )
        )

        self.setup_file_synchronizer = (
            SetupFileSynchronizer()
        )

        self.setup_file_template_provider = (
            SetupFileTemplateProvider(
                parser=self.vdproj_block_parser,
            )
        )

        self.vdproj_file_modifier = (
            VdprojFileModifier(
                parser=self.vdproj_block_parser,
            )
        )

        self.vdproj_component_identity_generator = (
            VdprojComponentIdentityGenerator()
        )

        self.vdproj_file_block_builder = (
            VdprojFileBlockBuilder()
        )

        self.vdproj_file_block_inserter = (
            VdprojFileBlockInserter()
        )

        self.setup_file_change_applier = (
            SetupFileChangeApplier(
                modifier=(
                    self.vdproj_file_modifier
                ),
                template_provider=(
                    self.setup_file_template_provider
                ),
                identity_generator=(
                    self.vdproj_component_identity_generator
                ),
                block_builder=(
                    self.vdproj_file_block_builder
                ),
                block_inserter=(
                    self.vdproj_file_block_inserter
                ),
            )
        )

        self.setup_workspace_service = (
            SetupWorkspaceService()
        )

        self.temporary_solution_service = (
            TemporarySolutionService()
        )
        self.setup_project_preparer = (
            SetupProjectPreparer(
                workspace_service=(
                    self.setup_workspace_service
                ),
                setup_file_loader=(
                    self.vdproj_setup_file_loader
                ),
                synchronizer=(
                    self.setup_file_synchronizer
                ),
                change_applier=(
                    self.setup_file_change_applier
                ),
            )
        )

        self.setup_orchestrator = (
            DefaultSetupOrchestrator(
                workspace_resolver=(
                    self.workspace_resolver
                ),
                setup_path_resolver=(
                    self.setup_path_resolver
                ),
                advanced_installer_definition_loader=(
                    self.advanced_installer_setup_definition_loader
                ),
                setup_factory=(
                    self.setup_factory
                ),
                settings=(
                    self.settings
                ),
            )
        )

        self.execute_setup_use_case = (
            DefaultExecuteSetupUseCase(
                setup_orchestrator=(
                    self.setup_orchestrator
                ),
            )
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
                build_context_factory=self.build_context_factory,
                publish_context_factory=self.publish_context_factory,
                pipeline_factory=self.pipeline_factory,
                solution_locator=self.solution_locator_service,
                pipeline_runner=self.pipeline_runner,
                project_repository=self.project_repository,
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
        Cria e configura a aplicaÃ§Ã£o.
        """

        app = FastAPI(
            title="OuroBuild",
            description="Sistema interno de automaÃ§Ã£o de builds da OuroWeb",
            version=self.settings.version,
        )

        #
        # Tratamento global de exceÃ§Ãµes
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
