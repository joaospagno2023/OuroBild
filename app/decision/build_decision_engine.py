"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_decision_engine.py
Descrição : Responsável por decidir como um projeto deve ser
            construído a partir do resultado da análise.
--------------------------------------------------------------------
"""

from app.models.analyzers.analysis_result import (
    AnalysisResult,
)

from app.models.decision.build_decision import (
    BuildDecision,
)


class BuildDecisionEngine:
    """
    Responsável por transformar o resultado da
    análise em um plano de execução do Build.
    """

    def create(
        self,
        analysis: AnalysisResult,
    ) -> BuildDecision:
        """
        Cria um plano de execução do Build.
        """

        decision = BuildDecision()

        #
        # Framework
        #

        decision.sdk_style = (
            analysis.framework.sdk_style
        )

        if decision.sdk_style:

            decision.builder = "dotnet"

            decision.restore_packages = True

        else:

            decision.builder = "msbuild"

        #
        # Build
        #

        decision.sign_assembly = (
            analysis.build.sign_assembly
        )

        decision.executable = (
            analysis.build.output_type
            in (
                "Exe",
                "WinExe",
            )
        )

        #
        # Plano inicial
        #

        if decision.restore_packages:

            decision.execution_plan.append(
                "restore",
            )

        decision.execution_plan.append(
            "build",
        )

        if decision.publish_after_build:

            decision.execution_plan.append(
                "publish",
            )

        return decision