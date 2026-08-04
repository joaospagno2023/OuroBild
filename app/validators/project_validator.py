"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_validator.py
Descrição : Responsável por validar um ProjectProfile.
--------------------------------------------------------------------
"""

from app.models.analyzers.diagnostic import (
    Diagnostic,
)
from app.models.analyzers.diagnostic_codes import (
    DiagnosticCode,
)
from app.models.analyzers.project_profile import (
    ProjectProfile,
)
from app.validators.base_validator import (
    BaseValidator,
)


class ProjectValidator(
    BaseValidator,
):
    """
    Responsável por validar um ProjectProfile.
    """

    def validate(
        self,
        project: ProjectProfile,
    ) -> list[Diagnostic]:

        diagnostics: list[
            Diagnostic
        ] = []

        #
        # AssemblyName
        #

        if not project.assembly_name:

            diagnostics.append(

                self.create_error(

                    code=DiagnosticCode.PROJECT_ASSEMBLY_NAME_MISSING,

                    message="AssemblyName não informado.",
                )
            )

        #
        # RootNamespace
        #

        if not project.root_namespace:

            diagnostics.append(

                self.create_error(

                    code=DiagnosticCode.PROJECT_ROOT_NAMESPACE_MISSING,

                    message="RootNamespace não informado.",
                )
            )

        #
        # ProjectGuid
        #

        if not project.project_guid:

            diagnostics.append(

                self.create_error(

                    code=DiagnosticCode.PROJECT_GUID_MISSING,

                    message="ProjectGuid não informado.",
                )
            )

        return diagnostics