"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_result.py
Descrição : Resultado de uma compilação.
--------------------------------------------------------------------
"""

from pydantic import BaseModel

from app.models.build.build_status import BuildStatus
from app.models.process.process_result import ProcessResult


class BuildResult(BaseModel):
    """
    Resultado final da compilação.
    """

    status: BuildStatus

    process: ProcessResult