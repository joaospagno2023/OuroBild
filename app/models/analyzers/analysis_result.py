"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : analysis_result.py
Descrição : Representa o resultado completo da análise de um projeto.
--------------------------------------------------------------------
"""

from dataclasses import dataclass, field

from app.models.analyzers.analysis_status import (
    AnalysisStatus,
)
from app.models.analyzers.build_profile import (
    BuildProfile,
)
from app.models.analyzers.diagnostic import (
    Diagnostic,
)
from app.models.analyzers.framework_profile import (
    FrameworkProfile,
)
from app.models.analyzers.project_profile import (
    ProjectProfile,
)
from app.models.analyzers.recommendation import (
    Recommendation,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AnalysisResult:
    """
    Representa o resultado completo
    da análise de um projeto.
    """

    status: AnalysisStatus

    project: ProjectProfile

    framework: FrameworkProfile

    build: BuildProfile

    diagnostics: list[Diagnostic] = field(
        default_factory=list,
    )

    recommendations: list[
        Recommendation
    ] = field(
        default_factory=list,
    )