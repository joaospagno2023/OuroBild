"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_root_api.py
Descrição : Testes do endpoint raiz da API.
--------------------------------------------------------------------
"""


def test_root_should_return_application_information(client):
    """
    Deve retornar as informações da aplicação.
    """

    #
    # Act
    #

    response = client.get("/")

    #
    # Assert
    #

    assert response.status_code == 200

    body = response.json()

    assert "application" in body
    assert "version" in body
    assert "status" in body

    assert body["status"] == "running"