"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_analyze_api.py
Descrição : Testes do endpoint POST /analyzes.
--------------------------------------------------------------------
"""


def test_execute_analyze_should_return_success(client):
    """
    Deve executar uma análise de projeto.
    """

    #
    # Arrange
    #

    payload = {
        "project": "linkpagamento",
        "environment": "production",
    }

    #
    # Act
    #

    response = client.post(
        "/analyzes",
        json=payload,
    )

    #
    # Assert
    #

    assert response.status_code == 200

    body = response.json()

    assert isinstance(
        body,
        dict,
    )

    #
    # O contrato será validado
    # na próxima evolução do teste.
    #