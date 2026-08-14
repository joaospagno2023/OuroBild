"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_definition.py
Descrição : Define as informações necessárias para geração
            de um Setup de um projeto.
--------------------------------------------------------------------
"""

from pathlib import Path

from pydantic import BaseModel


class SetupDefinition(
    BaseModel,
):
    """
    Representa a definição de um Setup.

    A definição contém as informações comuns necessárias
    para identificar e gerar o Setup de um projeto.

    Características específicas de cada tecnologia
    (.vdproj, .aip, etc.) serão tratadas pelos respectivos
    mecanismos de geração.
    """

    project_id: str

    name: str

    product_name: str

    manufacturer: str

    version: str

    configuration: str

    platform: str

    solution_path: Path

    setup_project_path: Path

    output_msi: Path