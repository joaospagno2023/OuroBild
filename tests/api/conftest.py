"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : conftest.py
Descrição : Configuração compartilhada dos testes da API.
--------------------------------------------------------------------
"""

import pytest
from fastapi.testclient import TestClient

from app.bootstrap import Bootstrap


@pytest.fixture(scope="session")
def app():
    """
    Cria uma única instância da aplicação
    para toda a suíte de testes da API.
    """

    bootstrap = Bootstrap()

    return bootstrap.create_app()


@pytest.fixture(scope="session")
def client(app):
    """
    Cliente HTTP utilizado pelos testes.
    """

    return TestClient(app)