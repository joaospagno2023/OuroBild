"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_path_resolver.py
Descrição : Resolve os caminhos utilizados na geração do Setup.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.models.project.project import (
    Project,
)

from app.models.setup.setup_paths import (
    SetupPaths,
)


class SetupPathResolver:
    """
    Resolve os caminhos necessários para geração do Setup.

    Regras:

    publish_path
        É obtido do Project.publish_path e considerado
        relativo à raiz física do projeto quando não for
        um caminho absoluto.

    aip_path
        É obtido do Project.aip_path e considerado relativo
        à raiz física do projeto quando não for absoluto.

    output_msi
        É obtido do Project.output_msi.

    installer_path
        É a pasta configurada nas configurações do OuroBuild
        onde os instaladores serão armazenados.
    """

    def resolve(
        self,
        project: Project,
        project_root: Path,
        installer_root: Path,
    ) -> SetupPaths:
        """
        Resolve todos os caminhos necessários para o Setup.

        Args:
            project:
                Projeto configurado no projects.json.

            project_root:
                Diretório físico onde o projeto está localizado.

            installer_root:
                Diretório configurado em settings.json
                para armazenamento dos instaladores.

        Returns:
            SetupPaths contendo os caminhos resolvidos.

        Raises:
            ValueError:
                Quando alguma informação obrigatória não
                for informada.
        """

        #
        # Validações básicas
        #

        if project is None:
            raise ValueError(
                "O projeto não foi informado."
            )

        if project_root is None:
            raise ValueError(
                "A raiz do projeto não foi informada."
            )

        if installer_root is None:
            raise ValueError(
                "A raiz dos instaladores não foi informada."
            )

        project_root = Path(
            project_root,
        )

        installer_root = Path(
            installer_root,
        )

        #
        # Publish
        #

        publish_path = (
            self.__resolve_project_path(
                value=project.publish_path,
                project_root=project_root,
                field_name="publish_path",
            )
        )

        #
        # Advanced Installer
        #

        aip_path = (
            self.__resolve_project_path(
                value=project.aip_path,
                project_root=project_root,
                field_name="aip_path",
            )
        )

        #
        # Nome do MSI
        #

        output_msi = (
            self.__resolve_output_msi(
                value=project.output_msi,
                installer_path=installer_root,
            )
        )

        #
        # Pasta dos instaladores
        #

        resolved_installer_path = (
            installer_root
        )

        #
        # Cria a estrutura de diretórios
        # necessária para o Setup.
        #

        resolved_installer_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        #
        # Garante que o diretório de
        # publicação exista.
        #

        publish_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        #
        # Garante que o diretório do
        # Advanced Installer exista.
        #
        # Se aip_path representar um arquivo
        # .aip, criamos somente o diretório pai.
        #

        if aip_path.suffix.lower() == ".aip":

            aip_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

        else:

            aip_path.mkdir(
                parents=True,
                exist_ok=True,
            )

        #
        # Retorna os caminhos resolvidos.
        #

        return SetupPaths(
            publish_path=publish_path,
            setup_output_path=resolved_installer_path,
            output_msi=output_msi,
            aip_path=aip_path,
        )

    def __resolve_project_path(
        self,
        value: str,
        project_root: Path,
        field_name: str,
    ) -> Path:
        """
        Resolve um caminho configurado no Project.

        Caminhos absolutos são respeitados.

        Caminhos relativos são considerados relativos
        à raiz física do projeto.
        """

        if not value or not value.strip():

            raise ValueError(
                f"O projeto não possui "
                f"{field_name} configurado."
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
            project_root / path
        )

    def __resolve_output_msi(
        self,
        value: str,
        installer_path: Path,
    ) -> Path:
        """
        Resolve o arquivo MSI de saída.

        Se output_msi for absoluto, o caminho é respeitado.

        Caso contrário, o MSI será criado dentro da pasta
        configurada em installer_path.
        """

        if not value or not value.strip():

            raise ValueError(
                "O projeto não possui "
                "output_msi configurado."
            )

        output_msi = Path(
            value.strip(),
        )

        #
        # Se output_msi já for absoluto,
        # respeitamos a configuração.
        #

        if output_msi.is_absolute():

            return output_msi

        #
        # Normalmente output_msi será apenas
        # o nome do MSI.
        #

        return (
            installer_path / output_msi
        )