"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_not_found_exception.py
Descrição : Projeto não encontrado.
--------------------------------------------------------------------
"""

from app.exceptions.ourobuild_exception import OuroBuildException


class ProjectNotFoundException(
    OuroBuildException,
):
    """
    Projeto solicitado não foi encontrado.
    """

    pass