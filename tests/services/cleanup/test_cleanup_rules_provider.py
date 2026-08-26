"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_cleanup_rules_provider.py
Descrição : Testes do provedor de regras de limpeza.
--------------------------------------------------------------------
"""

from app.models.cleanup.cleanup_rule import (
    CleanupAction,
    CleanupTarget,
)

from app.services.cleanup.cleanup_rules_provider import (
    CleanupRulesProvider,
)


def test_deve_retornar_regras_globais():

    rules = (
        CleanupRulesProvider.get_rules()
    )

    assert len(rules) == 4

    assert any(
        rule.target == CleanupTarget.FILE
        and rule.pattern == "*.pdb"
        and rule.action
        == CleanupAction.REMOVE
        for rule in rules
    )

    assert any(
        rule.target == CleanupTarget.FILE
        and rule.pattern == "*.xml"
        and rule.action
        == CleanupAction.REMOVE
        for rule in rules
    )

    assert any(
        rule.target == CleanupTarget.FILE
        and rule.pattern == "*.config"
        and rule.action
        == CleanupAction.REMOVE
        for rule in rules
    )

    assert any(
        rule.target
        == CleanupTarget.DIRECTORY
        and rule.pattern == "*"
        and rule.action
        == CleanupAction.REMOVE
        for rule in rules
    )


def test_deve_retornar_regra_especifica_linkpagamento():

    rules = (
        CleanupRulesProvider.get_rules(
            project_id="linkpagamento",
        )
    )

    rule = next(
        rule
        for rule in rules
        if (
            rule.pattern
            == "OuroNetWinServiceLinkPagamento.exe.config"
        )
    )

    assert (
        rule.target
        == CleanupTarget.FILE
    )

    assert (
        rule.action
        == CleanupAction.PRESERVE
    )

    assert (
        rule.project_id
        == "linkpagamento"
    )


def test_deve_retornar_regra_especifica_movement():

    rules = (
        CleanupRulesProvider.get_rules(
            project_id="movement",
        )
    )

    rule = next(
        rule
        for rule in rules
        if rule.pattern == "XML"
    )

    assert (
        rule.target
        == CleanupTarget.DIRECTORY
    )

    assert (
        rule.action
        == CleanupAction.PRESERVE
    )

    assert (
        rule.project_id
        == "movement"
    )


def test_projeto_desconhecido_deve_receber_somente_regras_globais():

    rules = (
        CleanupRulesProvider.get_rules(
            project_id="projeto-inexistente",
        )
    )

    assert len(rules) == 4

    assert all(
        rule.project_id is None
        for rule in rules
    )


def test_deve_retornar_quatro_regras_globais():

    rules = (
        CleanupRulesProvider.get_rules()
    )

    global_rules = [
        rule
        for rule in rules
        if rule.project_id is None
    ]

    assert len(global_rules) == 4


def test_regra_global_de_diretorio_deve_remover():

    rules = (
        CleanupRulesProvider.get_rules()
    )

    rule = next(
        rule
        for rule in rules
        if (
            rule.target
            == CleanupTarget.DIRECTORY
            and rule.pattern == "*"
        )
    )

    assert (
        rule.action
        == CleanupAction.REMOVE
    )

    assert (
        rule.project_id
        is None
    )


def test_linkpagamento_deve_manter_regra_global_de_diretorio():

    rules = (
        CleanupRulesProvider.get_rules(
            project_id="linkpagamento",
        )
    )

    directory_rules = [
        rule
        for rule in rules
        if (
            rule.target
            == CleanupTarget.DIRECTORY
        )
    ]

    assert len(directory_rules) == 1

    rule = directory_rules[0]

    assert (
        rule.pattern
        == "*"
    )

    assert (
        rule.action
        == CleanupAction.REMOVE
    )

    assert (
        rule.project_id
        is None
    )


def test_movement_deve_ter_regra_global_e_excecao_xml():

    rules = (
        CleanupRulesProvider.get_rules(
            project_id="movement",
        )
    )

    directory_rules = [
        rule
        for rule in rules
        if (
            rule.target
            == CleanupTarget.DIRECTORY
        )
    ]

    assert len(directory_rules) == 2

    assert any(
        rule.pattern == "*"
        and rule.action
        == CleanupAction.REMOVE
        and rule.project_id is None
        for rule in directory_rules
    )

    assert any(
        rule.pattern == "XML"
        and rule.action
        == CleanupAction.PRESERVE
        and rule.project_id == "movement"
        for rule in directory_rules
    )