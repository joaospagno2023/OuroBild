"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_exception.py
Descrição : Exceção base da Pipeline.
--------------------------------------------------------------------
"""

from app.exceptions.ourobuild_exception import OuroBuildException


class PipelineException(OuroBuildException):
    """
    Exceção base da Engine de Pipeline.
    """

    pass