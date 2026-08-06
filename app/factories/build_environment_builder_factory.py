"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_environment_builder_factory.py
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
from app.services.workspace.solution_locator_service import (
    SolutionLocatorService,
)


class BuildEnvironmentBuilderFactory:

    def __init__(
        self,
        solution_locator: SolutionLocatorService,
    ) -> None:

        self.__solution_locator = (
            solution_locator
        )
   
    def create(
        self,
        environment: BuildEnvironment,
    ) -> BuildEnvironmentBuilder:

        match environment.resolver:

            case "versioned":
                print("USANDO VersionedBuildEnvironmentBuilder")

                return VersionedBuildEnvironmentBuilder(
                    solution_locator=self.__solution_locator,
                )

            case "production":
                print("USANDO ProductionBuildEnvironmentBuilder")
                
                return ProductionBuildEnvironmentBuilder(
                    solution_locator=self.__solution_locator,
                )

            case _:

                raise ValueError(
                    f"Resolver '{environment.resolver}' não suportado."
                )