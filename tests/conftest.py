"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : conftest.py
Descrição : Fixtures compartilhadas entre os testes.
--------------------------------------------------------------------
"""

import pytest


@pytest.fixture
def dummy():
    """
    Fixture inicial utilizada para validar a infraestrutura.
    """
    return True