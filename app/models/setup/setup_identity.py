"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_identity.py
Descrição : Representa a identidade de um Setup Visual Studio.
--------------------------------------------------------------------
"""

from uuid import UUID

from pydantic import BaseModel


class SetupIdentity(
    BaseModel,
):
    """
    Representa os identificadores de um Setup MSI.
    """

    product_code: UUID

    package_code: UUID

    upgrade_code: UUID