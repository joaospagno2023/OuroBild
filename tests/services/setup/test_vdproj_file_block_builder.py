"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_vdproj_file_block_builder.py
Descrição : Testes do VdprojFileBlockBuilder.
--------------------------------------------------------------------
"""

from app.services.setup.vdproj_component_identity_generator import (
    VdprojComponentIdentityGenerator,
)

from app.services.setup.vdproj_file_block_builder import (
    VdprojFileBlockBuilder,
)


TEMPLATE = """
"{9F6F8455-1EF1-4B85-886A-4223BCC8E7F7}:_4997131993751F0F4C2148899EEE6615"
{
    "AssemblyRegister" = "3:1"
    "AssemblyIsInGAC" = "11:FALSE"
    "AssemblyAsmDisplayName" = "8:Custom.Framework, Version=4.0.0.0"

    "ScatterAssemblies"
    {
        "_123456"
        {
            "Name" = "8:Custom.Framework.dll"
            "Attributes" = "3:512"
        }
    }

    "SourcePath" = "8:Custom.Framework.dll"
    "TargetName" = "8:"
    "Tag" = "8:"
    "Folder" = "8:_ABCDEF"
    "Condition" = "8:"
    "Transitive" = "11:FALSE"
    "Vital" = "11:TRUE"
}
"""


def create_identity():
    """
    Cria uma identidade de componente para o teste.
    """

    generator = (
        VdprojComponentIdentityGenerator()
    )

    return generator.generate()


def test_deve_criar_bloco_com_novo_arquivo():
    """
    Deve substituir o nome e o SourcePath do arquivo.
    """

    builder = (
        VdprojFileBlockBuilder()
    )

    identity = create_identity()

    result = builder.build(
        template=TEMPLATE,
        file_name="NovaBiblioteca.dll",
        source_path=(
            r"..\..\02-Source\NovaBiblioteca.dll"
        ),
        identity=identity,
    )

    assert (
        '"Name" = "8:NovaBiblioteca.dll"'
        in result
    )

    assert (
        '"SourcePath" = '
        '"8:..\\..\\02-Source\\NovaBiblioteca.dll"'
        in result
    )


def test_deve_atualizar_assembly_display_name():
    """
    Deve substituir o AssemblyAsmDisplayName.
    """

    builder = (
        VdprojFileBlockBuilder()
    )

    identity = create_identity()

    result = builder.build(
        template=TEMPLATE,
        file_name="NovaBiblioteca.dll",
        source_path="NovaBiblioteca.dll",
        identity=identity,
        assembly_display_name=(
            "NovaBiblioteca, Version=10.4.8.0, "
            "Culture=neutral, "
            "PublicKeyToken=81568928c6d92f5f, "
            "processorArchitecture=MSIL"
        ),
    )

    assert (
        '"AssemblyAsmDisplayName" = '
        '"8:NovaBiblioteca, Version=10.4.8.0, '
        'Culture=neutral, '
        'PublicKeyToken=81568928c6d92f5f, '
        'processorArchitecture=MSIL"'
        in result
    )


def test_deve_preservar_propriedades_do_template():
    """
    Deve preservar propriedades que não são alteradas.
    """

    builder = (
        VdprojFileBlockBuilder()
    )

    identity = create_identity()

    result = builder.build(
        template=TEMPLATE,
        file_name="NovaBiblioteca.dll",
        source_path="NovaBiblioteca.dll",
        identity=identity,
    )

    assert (
        '"AssemblyRegister" = "3:1"'
        in result
    )

    assert (
        '"AssemblyIsInGAC" = "11:FALSE"'
        in result
    )

    assert (
        '"Attributes" = "3:512"'
        in result
    )

    assert (
        '"TargetName" = "8:"'
        in result
    )

    assert (
        '"Vital" = "11:TRUE"'
        in result
    )


def test_deve_substituir_identidade_do_componente():
    """
    Deve substituir a identidade externa do componente.
    """

    builder = (
        VdprojFileBlockBuilder()
    )

    identity = create_identity()

    result = builder.build(
        template=TEMPLATE,
        file_name="NovaBiblioteca.dll",
        source_path="NovaBiblioteca.dll",
        identity=identity,
    )

    assert (
        f'"{identity.key}"'
        in result
    )

    assert (
        "9F6F8455-1EF1-4B85-886A-4223BCC8E7F7"
        not in result
    )

    assert (
        "_4997131993751F0F4C2148899EEE6615"
        not in result
    )