"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : sql_application_configuration_repository.py
Descrição : Repositório da configuração utilizando SQL Server.
--------------------------------------------------------------------
"""

from datetime import (
    datetime,
    timezone,
)

from sqlalchemy import (
    select,
)

from app.abstractions.application_configuration_repository import (
    ApplicationConfigurationRepository,
)

from app.database.connection import (
    DatabaseConnection,
)

from app.database.models.application_configuration_model import (
    ApplicationConfigurationModel,
)

from app.models.configuration.app_settings import (
    AppSettings,
)


class SqlApplicationConfigurationRepository(
    ApplicationConfigurationRepository,
):
    """
    Implementação do repositório de configuração para SQL Server.
    """

    CONFIGURATION_ID = 1

    def __init__(
        self,
        database_connection: DatabaseConnection,
    ) -> None:
        """
        Inicializa o repositório.

        Args:
            database_connection:
                Conexão com o banco de dados.
        """

        if database_connection is None:
            raise ValueError(
                "DatabaseConnection não foi informado."
            )

        self.__database_connection = (
            database_connection
        )

    def get(
        self,
    ) -> AppSettings | None:
        """
        Retorna a configuração persistida.

        Returns:
            AppSettings ou None quando não existir.
        """

        with self.__database_connection.create_session() as session:

            statement = (
                select(
                    ApplicationConfigurationModel
                )
                .where(
                    ApplicationConfigurationModel.id
                    == self.CONFIGURATION_ID
                )
            )

            configuration_model = (
                session.scalars(
                    statement
                )
                .first()
            )

            if configuration_model is None:
                return None

            return self.__to_settings(
                configuration_model
            )

    def save(
        self,
        settings: AppSettings,
    ) -> AppSettings:
        """
        Persiste a configuração.

        Quando o registro Id=1 já existe, ele é atualizado.
        Caso contrário, um novo registro é criado.

        Args:
            settings:
                Configuração completa da aplicação.

        Returns:
            Configuração persistida.
        """

        if settings is None:
            raise ValueError(
                "AppSettings não foi informado."
            )

        with self.__database_connection.create_session() as session:

            statement = (
                select(
                    ApplicationConfigurationModel
                )
                .where(
                    ApplicationConfigurationModel.id
                    == self.CONFIGURATION_ID
                )
            )

            configuration_model = (
                session.scalars(
                    statement
                )
                .first()
            )

            now = datetime.now(
                timezone.utc
            )

            if configuration_model is None:

                configuration_model = (
                    ApplicationConfigurationModel(
                        id=self.CONFIGURATION_ID,
                        application_name=(
                            settings.application_name
                        ),
                        version=settings.version,
                        log_level=settings.log_level,
                        base_path=str(
                            settings.base_path
                        ),
                        installer_path=str(
                            settings.installer_path
                        ),
                        publish_path=str(
                            settings.publish_path
                        ),
                        msbuild_path=str(
                            settings.build_tools.msbuild_path
                        ),
                        advanced_installer_path=str(
                            settings.build_tools.advanced_installer_path
                        ),
                        robocopy_path=str(
                            settings.build_tools.robocopy_path
                        ),
                        setup_engine=(
                            settings.setup.engine.value
                        ),
                        setup_output_root=str(
                            settings.setup.output_root
                        ),
                        setup_aip_root=str(
                            settings.setup.aip_root
                        ),
                        setup_excluir_pasta_work=(
                            settings.setup.excluirpastawork
                        ),
                        logging_enabled=(
                            settings.logging.enabled
                        ),
                        logging_path=str(
                            settings.logging.path
                        ),
                        logging_level=(
                            settings.logging.level
                        ),
                        storage_workspace_path=str(
                            settings.storage.workspace_path
                        ),
                        jwt_secret=(
                            settings.security.jwt_secret
                        ),
                        jwt_algorithm=(
                            settings.security.jwt_algorithm
                        ),
                        token_expiration_minutes=(
                            settings.security.token_expiration_minutes
                        ),
                        created_at=now,
                        updated_at=now,
                    )
                )

                session.add(
                    configuration_model
                )

            else:

                configuration_model.application_name = (
                    settings.application_name
                )

                configuration_model.version = (
                    settings.version
                )

                configuration_model.log_level = (
                    settings.log_level
                )

                configuration_model.base_path = str(
                    settings.base_path
                )

                configuration_model.installer_path = str(
                    settings.installer_path
                )

                configuration_model.publish_path = str(
                    settings.publish_path
                )

                configuration_model.msbuild_path = str(
                    settings.build_tools.msbuild_path
                )

                configuration_model.advanced_installer_path = str(
                    settings.build_tools.advanced_installer_path
                )

                configuration_model.robocopy_path = str(
                    settings.build_tools.robocopy_path
                )

                configuration_model.setup_engine = (
                    settings.setup.engine.value
                )

                configuration_model.setup_output_root = str(
                    settings.setup.output_root
                )

                configuration_model.setup_aip_root = str(
                    settings.setup.aip_root
                )

                configuration_model.setup_excluir_pasta_work = (
                    settings.setup.excluirpastawork
                )

                configuration_model.logging_enabled = (
                    settings.logging.enabled
                )

                configuration_model.logging_path = str(
                    settings.logging.path
                )

                configuration_model.logging_level = (
                    settings.logging.level
                )

                configuration_model.storage_workspace_path = str(
                    settings.storage.workspace_path
                )

                configuration_model.jwt_secret = (
                    settings.security.jwt_secret
                )

                configuration_model.jwt_algorithm = (
                    settings.security.jwt_algorithm
                )

                configuration_model.token_expiration_minutes = (
                    settings.security.token_expiration_minutes
                )

                configuration_model.updated_at = now

            session.flush()

            result = self.__to_settings(
                configuration_model
            )

            session.commit()

            return result

    def __to_settings(
        self,
        model: ApplicationConfigurationModel,
    ) -> AppSettings:
        """
        Converte o modelo SQLAlchemy para AppSettings.
        """

        from app.models.configuration.build_tools_settings import (
            BuildToolsSettings,
        )

        from app.models.configuration.logging_settings import (
            LoggingSettings,
        )

        from app.models.configuration.security_settings import (
            SecuritySettings,
        )

        from app.models.configuration.setup_settings import (
            SetupSettings,
        )

        from app.models.configuration.storage_settings import (
            StorageSettings,
        )

        from app.models.setup.setup_engine import (
            SetupEngine,
        )

        return AppSettings(
            application_name=(
                model.application_name
            ),
            version=model.version,
            log_level=model.log_level,
            base_path=model.base_path,
            installer_path=model.installer_path,
            publish_path=model.publish_path,
            storage=StorageSettings(
                root_path=model.storage_workspace_path,
            ),
            build_tools=BuildToolsSettings(
                msbuild_path=model.msbuild_path,
                advanced_installer_path=(
                    model.advanced_installer_path
                ),
                robocopy_path=model.robocopy_path,
            ),
            setup=SetupSettings(
                engine=SetupEngine(
                    model.setup_engine
                ),
                output_root=model.setup_output_root,
                aip_root=model.setup_aip_root,
                excluirpastawork=(
                    model.setup_excluir_pasta_work
                ),
            ),
            logging=LoggingSettings(
                enabled=model.logging_enabled,
                path=model.logging_path,
                level=model.logging_level,
            ),
            security=SecuritySettings(
                jwt_secret=model.jwt_secret,
                jwt_algorithm=model.jwt_algorithm,
                token_expiration_minutes=(
                    model.token_expiration_minutes
                ),
            ),
            database=(
                self.__database_connection.settings
            ),
        )