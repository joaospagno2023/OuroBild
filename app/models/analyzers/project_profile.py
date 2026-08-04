"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_profile.py
Descrição : Representa a identidade de um projeto analisado.
--------------------------------------------------------------------
"""

from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class ProjectProfile:
    """
    Representa a identidade técnica de um projeto.
    """

    name: str = ""

    assembly_name: str = ""

    root_namespace: str = ""

    project_guid: str = ""

    output_type: str = ""