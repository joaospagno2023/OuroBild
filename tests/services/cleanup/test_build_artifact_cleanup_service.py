"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_build_artifact_cleanup_service.py
Descrição : Testes do serviço de limpeza dos artefatos do Build.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.models.cleanup.cleanup_rule import (
    CleanupAction,
    CleanupRule,
    CleanupTarget,
)

from app.services.cleanup.build_artifact_cleanup_service import (
    BuildArtifactCleanupService,
)


def create_file(
    path: Path,
    content: str = "teste",
) -> Path:
    """
    Cria um arquivo de teste.
    """

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        content,
        encoding="utf-8",
    )

    return path


def create_service() -> BuildArtifactCleanupService:
    """
    Cria o serviço utilizando as regras globais padrão.
    """

    return BuildArtifactCleanupService(
        rules=[
            CleanupRule(
                target=CleanupTarget.FILE,
                pattern="*.pdb",
                action=CleanupAction.REMOVE,
            ),
            CleanupRule(
                target=CleanupTarget.FILE,
                pattern="*.xml",
                action=CleanupAction.REMOVE,
            ),
            CleanupRule(
                target=CleanupTarget.FILE,
                pattern="*.config",
                action=CleanupAction.REMOVE,
            ),
        ],
    )


def test_deve_remover_arquivos_pdb(
    tmp_path: Path,
):
    """
    Deve remover arquivos .pdb.
    """

    pdb_file = create_file(
        tmp_path / "Teste.pdb",
    )

    service = create_service()

    result = service.execute(
        workspace_path=tmp_path,
    )

    assert not pdb_file.exists()

    assert pdb_file in result.files_removed

    assert result.success


def test_deve_remover_arquivos_xml(
    tmp_path: Path,
):
    """
    Deve remover arquivos .xml.
    """

    xml_file = create_file(
        tmp_path / "Teste.xml",
    )

    service = create_service()

    result = service.execute(
        workspace_path=tmp_path,
    )

    assert not xml_file.exists()

    assert xml_file in result.files_removed

    assert result.success


def test_deve_preservar_appsettings_json(
    tmp_path: Path,
):
    """
    appsettings.json não deve ser removido.
    """

    appsettings = create_file(
        tmp_path / "appsettings.json",
    )

    service = create_service()

    result = service.execute(
        workspace_path=tmp_path,
    )

    assert appsettings.exists()

    assert (
        appsettings
        in result.files_preserved
    )

    assert result.success


def test_deve_preservar_config_principal_do_executavel(
    tmp_path: Path,
):
    """
    O arquivo .exe.config principal deve ser preservado
    através de uma regra específica.
    """

    config_file = create_file(
        tmp_path
        / "OuroNetWinServiceLinkPagamento.exe.config",
    )

    service = BuildArtifactCleanupService(
        rules=[
            CleanupRule(
                target=CleanupTarget.FILE,
                pattern="*.config",
                action=CleanupAction.REMOVE,
            ),
            CleanupRule(
                target=CleanupTarget.FILE,
                pattern=(
                    "OuroNetWinServiceLinkPagamento.exe.config"
                ),
                action=CleanupAction.PRESERVE,
                project_id="linkpagamento",
            ),
        ],
    )

    result = service.execute(
        workspace_path=tmp_path,
        project_id="linkpagamento",
    )

    assert config_file.exists()

    assert (
        config_file
        in result.files_preserved
    )

    assert (
        config_file
        not in result.files_removed
    )

    assert result.success


def test_deve_preservar_pasta_xml_mas_remover_arquivos_xml(
    tmp_path: Path,
):
    """
    Deve preservar a pasta XML e todo o seu conteúdo
    através de uma regra específica do projeto.

    Uma pasta preservada protege seus arquivos e
    subdiretórios contra as regras globais de remoção.
    """

    xml_directory = (
        tmp_path
        / "bin"
        / "XML"
    )

    xml_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    xml_file = create_file(
        xml_directory
        / "Movimentos.xml",
    )

    service = BuildArtifactCleanupService(
        rules=[
            CleanupRule(
                target=CleanupTarget.FILE,
                pattern="*.xml",
                action=CleanupAction.REMOVE,
            ),
            CleanupRule(
                target=CleanupTarget.DIRECTORY,
                pattern="XML",
                action=CleanupAction.PRESERVE,
                project_id="movement",
            ),
        ],
    )

    result = service.execute(
        workspace_path=tmp_path,
        project_id="movement",
    )

    #
    # A pasta deve permanecer.
    #

    assert xml_directory.exists()

    #
    # O XML deve permanecer porque está dentro de uma
    # pasta preservada.
    #

    assert xml_file.exists()
    #
    # O arquivo deve aparecer na lista de preservados.
    #

    assert (
        xml_file
        in result.files_preserved
    )

    #
    # A pasta deve aparecer como preservada.
    #

    assert (
        xml_directory
        in result.directories_preserved
    )

    assert result.success


def test_deve_preservar_arquivo_nao_xml_dentro_de_pasta_xml(
    tmp_path: Path,
):
    """
    Deve preservar todo o conteúdo de uma pasta
    preservada, independentemente da extensão dos arquivos.
    """

    xml_directory = (
        tmp_path
        / "bin"
        / "XML"
    )

    xml_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    xml_file = create_file(
        xml_directory
        / "Movimentos.xml",
    )

    data_file = create_file(
        xml_directory
        / "dados.dat",
    )

    service = BuildArtifactCleanupService(
        rules=[
            CleanupRule(
                target=CleanupTarget.FILE,
                pattern="*.xml",
                action=CleanupAction.REMOVE,
            ),
            CleanupRule(
                target=CleanupTarget.DIRECTORY,
                pattern="XML",
                action=CleanupAction.PRESERVE,
                project_id="movement",
            ),
        ],
    )

    result = service.execute(
        workspace_path=tmp_path,
        project_id="movement",
    )

    #
    # A pasta deve permanecer.
    #

    assert xml_directory.exists()

    #
    # O XML deve permanecer porque está dentro de uma
    # pasta preservada.
    #

    assert xml_file.exists()

    #
    # O arquivo sem regra deve permanecer.
    #

    assert data_file.exists()

   #
    # Validação dos resultados.
    #

    assert (
        xml_file
        in result.files_preserved
    )

    assert (
        data_file
        in result.files_preserved
    )

    assert (
        xml_directory
        in result.directories_preserved
    )

    assert result.success


def test_deve_funcionar_em_dry_run(
    tmp_path: Path,
):
    """
    Dry run deve identificar os arquivos
    sem removê-los.
    """

    pdb_file = create_file(
        tmp_path / "Teste.pdb",
    )

    xml_file = create_file(
        tmp_path / "Teste.xml",
    )

    service = create_service()

    result = service.execute(
        workspace_path=tmp_path,
        dry_run=True,
    )

    assert pdb_file.exists()

    assert xml_file.exists()

    assert pdb_file in result.files_removed

    assert xml_file in result.files_removed

    assert result.dry_run

    assert result.success


def test_deve_contar_arquivos_analisados(
    tmp_path: Path,
):
    """
    Deve contabilizar os arquivos analisados.
    """

    create_file(
        tmp_path / "Teste.pdb",
    )

    create_file(
        tmp_path / "Teste.xml",
    )

    create_file(
        tmp_path / "Teste.txt",
    )

    service = create_service()

    result = service.execute(
        workspace_path=tmp_path,
    )

    assert result.files_analyzed == 3


def test_deve_preservar_arquivo_sem_regra(
    tmp_path: Path,
):
    """
    Arquivos que não possuem regra devem permanecer.
    """

    txt_file = create_file(
        tmp_path / "Teste.txt",
    )

    service = create_service()

    result = service.execute(
        workspace_path=tmp_path,
    )

    assert txt_file.exists()

    assert (
        txt_file
        in result.files_preserved
    )

    assert result.success


def test_deve_remover_diretorio_vazio(
    tmp_path: Path,
):
    """
    Deve remover um diretório vazio
    quando existir uma regra específica.
    """

    directory = (
        tmp_path
        / "Temp"
    )

    directory.mkdir()

    service = BuildArtifactCleanupService(
        rules=[
            CleanupRule(
                target=CleanupTarget.DIRECTORY,
                pattern="Temp",
                action=CleanupAction.REMOVE,
            ),
        ],
    )

    result = service.execute(
        workspace_path=tmp_path,
    )

    assert not directory.exists()

    assert (
        directory
        in result.directories_removed
    )

    assert result.success


def test_deve_preservar_diretorio_especifico_do_projeto(
    tmp_path: Path,
):
    """
    Deve priorizar a regra específica do projeto
    sobre a regra global.
    """

    directory = (
        tmp_path
        / "XML"
    )

    directory.mkdir()

    service = BuildArtifactCleanupService(
        rules=[
            CleanupRule(
                target=CleanupTarget.DIRECTORY,
                pattern="XML",
                action=CleanupAction.PRESERVE,
                project_id="movement",
            ),
            CleanupRule(
                target=CleanupTarget.DIRECTORY,
                pattern="XML",
                action=CleanupAction.REMOVE,
            ),
        ],
    )

    result = service.execute(
        workspace_path=tmp_path,
        project_id="movement",
    )

    assert directory.exists()

    assert (
        directory
        in result.directories_preserved
    )

    assert (
        directory
        not in result.directories_removed
    )

    assert result.success


def test_deve_aplicar_regra_global_quando_nao_houver_regra_do_projeto(
    tmp_path: Path,
):
    """
    Deve utilizar a regra global quando não existir
    uma regra específica para o projeto.
    """

    directory = (
        tmp_path
        / "Temp"
    )

    directory.mkdir()

    service = BuildArtifactCleanupService(
        rules=[
            CleanupRule(
                target=CleanupTarget.DIRECTORY,
                pattern="Temp",
                action=CleanupAction.REMOVE,
            ),
        ],
    )

    result = service.execute(
        workspace_path=tmp_path,
        project_id="movement",
    )

    assert not directory.exists()

    assert (
        directory
        in result.directories_removed
    )

    assert result.success


def test_deve_priorizar_regra_do_projeto_sobre_regra_global(
    tmp_path: Path,
):
    """
    A regra específica do projeto deve possuir
    prioridade sobre a regra global.
    """

    directory = (
        tmp_path
        / "XML"
    )

    directory.mkdir()

    service = BuildArtifactCleanupService(
        rules=[
            CleanupRule(
                target=CleanupTarget.DIRECTORY,
                pattern="XML",
                action=CleanupAction.PRESERVE,
                project_id="movement",
            ),
            CleanupRule(
                target=CleanupTarget.DIRECTORY,
                pattern="XML",
                action=CleanupAction.REMOVE,
            ),
        ],
    )

    result = service.execute(
        workspace_path=tmp_path,
        project_id="movement",
    )

    assert directory.exists()

    assert (
        directory
        in result.directories_preserved
    )

    assert (
        directory
        not in result.directories_removed
    )

    assert result.success


def test_deve_rejeitar_workspace_inexistente(
    tmp_path: Path,
):
    """
    Deve rejeitar um workspace inexistente.
    """

    service = create_service()

    workspace = (
        tmp_path
        / "nao-existe"
    )

    try:

        service.execute(
            workspace_path=workspace,
        )

        assert False

    except ValueError as error:

        assert (
            str(error)
            == "Workspace do Build não existe."
        )