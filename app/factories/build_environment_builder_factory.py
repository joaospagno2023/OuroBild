"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_environment_builder_factory.py
Descrição : Responsável por selecionar o Builder adequado para o
             ambiente de Build.
--------------------------------------------------------------------
"""

from app.abstractions.build_environment_builder import (
    BuildEnvironmentBuilder,
)
from app.builders.production_build_environment_builder import (
    ProductionBuildEnvironmentBuilder,
)
from app.builders.versioned_build_environment_builder import (
    VersionedBuildEnvironmentBuilder,
)
from app.models.environment.build_environment import (
    BuildEnvironment,
)


class BuildEnvironmentBuilderFactory:
    """
    Seleciona o Builder de acordo com o ambiente.
    """

    def create(
        self,
        environment: BuildEnvironment,
    ) -> BuildEnvironmentBuilder:

        match environment.resolver:

            case "versioned":
                return VersionedBuildEnvironmentBuilder()

            case "production":
                return ProductionBuildEnvironmentBuilder()

            case _:
                raise ValueError(
                    f"Resolver '{environment.resolver}' não suportado."
                )