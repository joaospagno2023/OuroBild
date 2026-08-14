"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_path_resolver.py
Descrição : Resolve o caminho utilizado para o Publish.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.models.project.project import (
    Project,
)


class PublishPathResolver:
    """
    Resolve o caminho de Publish configurado no projeto.

    Regras:

    publish_path
        É obtido do Project.publish_path.

        Quando for um caminho absoluto, o caminho é respeitado.

        Quando for um caminho relativo, ele é considerado
        relativo à raiz física do projeto.
    """

    def resolve(
        self,
        project: Project,
        project_root: Path,
    ) -> Path:
        """
        Resolve o caminho físico do Publish.

        Args:
            project:
                Projeto configurado no projects.json.

            project_root:
                Diretório físico onde o projeto está localizado.

        Returns:
            Caminho absoluto do diretório de Publish.

        Raises:
            ValueError:
                Quando publish_path não estiver configurado.
        """

        if project is None:
            raise ValueError(
                "O projeto não foi informado."
            )

        if project_root is None:
            raise ValueError(
                "A raiz do projeto não foi informada."
            )

        value = project.publish_path

        if not value or not value.strip():

            raise ValueError(
                "O projeto não possui "
                "publish_path configurado."
            )

        path = Path(
            value.strip(),
        )

        #
        # Caminho absoluto.
        #

        if path.is_absolute():

            return path

        #
        # Caminho relativo ao projeto.
        #

        return (
            Path(project_root)
            / path
        )