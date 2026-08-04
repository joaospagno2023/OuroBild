"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : analysis_context.py
Descrição : Contexto utilizado durante a análise de um projeto.
--------------------------------------------------------------------
"""

from dataclasses import dataclass

from app.models.analyzers.build_profile import (
    BuildProfile,
)
from app.models.analyzers.framework_profile import (
    FrameworkProfile,
)
from app.models.analyzers.project_profile import (
    ProjectProfile,
)


@dataclass(
    slots=True,
)
class AnalysisContext:
    """
    Armazena os resultados intermediários
    produzidos durante a análise.
    """

    project: ProjectProfile

    framework: FrameworkProfile

    build: BuildProfile