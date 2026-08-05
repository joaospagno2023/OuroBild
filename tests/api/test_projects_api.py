"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_projects_api.py
Descrição : Testes do endpoint GET /projects.
--------------------------------------------------------------------
"""


def test_get_projects_should_return_success(client):
    """
    Deve retornar a lista de projetos.
    """

    #
    # Act
    #

    response = client.get(
        "/projects",
    )

    #
    # Assert
    #

    assert response.status_code == 200

    body = response.json()

    assert isinstance(
        body,
        list,
    )