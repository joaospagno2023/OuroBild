"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_health_api.py
Descrição : Testes do endpoint /health.
--------------------------------------------------------------------
"""


def test_health_should_return_healthy(client):
    """
    Deve retornar o status da aplicação.
    """

    #
    # Act
    #

    response = client.get(
        "/health",
    )

    #
    # Assert
    #

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy",
    }