"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_document.py
Descrição : Representa um projeto MSBuild carregado em memória.
--------------------------------------------------------------------
"""

from pathlib import Path
from xml.etree.ElementTree import Element


class ProjectDocument:
    """
    Representa um arquivo .csproj carregado.

    Fornece métodos de alto nível para leitura das
    propriedades do projeto, escondendo os detalhes
    do XML dos Analyzers.
    """

    def __init__(
        self,
        file_path: Path,
        root: Element,
    ) -> None:

        self.file_path = file_path
        self.root = root

    @property
    def namespace(
        self,
    ) -> str:
        """
        Retorna o namespace padrão do XML.
        """

        if self.root.tag.startswith("{"):
            return self.root.tag.split("}")[0] + "}"

        return ""

    def get_property(
        self,
        name: str,
        default: str = "",
    ) -> str:
        """
        Retorna o valor de uma propriedade do projeto.
        """

        for property_group in self.root.findall(
            f"{self.namespace}PropertyGroup",
        ):

            element = property_group.find(
                f"{self.namespace}{name}",
            )

            if (
                element is not None
                and element.text is not None
            ):
                return element.text.strip()

        return default
    def get_attribute(
        self,
        name: str,
        default: str = "",
    ) -> str:
        """
        Retorna o valor de um atributo
        do elemento raiz do projeto.
        """

        value = self.root.attrib.get(name)

        if value is None:
            return default

        return value.strip()
    def has_property(
        self,
        name: str,
    ) -> bool:
        """
        Verifica se uma propriedade existe.
        """

        return self.get_property(
            name,
        ) != ""

    def get_property_bool(
        self,
        name: str,
        default: bool = False,
    ) -> bool:
        """
        Retorna uma propriedade booleana.
        """

        value = self.get_property(
            name,
        )

        if not value:
            return default

        return value.lower() in (
            "true",
            "1",
            "yes",
        )

    def find(
        self,
        xpath: str,
    ) -> Element | None:
        """
        Procura um elemento.
        """

        return self.root.find(
            xpath.replace(
                "./",
                f"./{self.namespace}",
            )
        )

    def findall(
        self,
        xpath: str,
    ) -> list[Element]:
        """
        Procura vários elementos.
        """

        return self.root.findall(
            xpath.replace(
                "./",
                f"./{self.namespace}",
            )
        )