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

from app.models.project.project_type import (
    ProjectType,
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

    Estrutura de saída:

        installer_root
            └── {version}.{revision}
                ├── Cliente
                └── Server
    """

    def resolve(
        self,
        project: Project,
        project_root: Path,
        installer_root: Path,
        workspace_root: Path | None = None,
        version: str | None = None,
        revision: int | None = None,
    ) -> SetupPaths:
        """
        Resolve todos os caminhos necessários para o Setup.

        Args:
            project:
                Projeto configurado no projects.json.

            project_root:
                Diretório físico onde o projeto está localizado.

            workspace_root:
                Diretório físico raiz do workspace.

            installer_root:
                Diretório configurado em settings.json
                para armazenamento dos instaladores.

            version:
                Versão do Setup.

            revision:
                Revisão do Setup.

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

        if workspace_root is None:
            workspace_root = project_root

        workspace_root = Path(
            workspace_root,
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
        visualstudio_setup_path = (
            self.__resolve_optional_workspace_path(
                value=project.visualstudio_setup_path,
                workspace_root=workspace_root,
            )
        )
        #
        # Pasta de saída dos instaladores
        #

        resolved_installer_path = (
            self.__resolve_installer_path(
                installer_root=installer_root,
                project=project,
                version=version,
                revision=revision,
            )
        )

        #
        # Nome do MSI
        #

        output_msi = (
            self.__resolve_output_msi(
                value=project.output_msi,
                installer_path=resolved_installer_path,
            )
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
            visualstudio_setup_path=visualstudio_setup_path,
        )

    def __resolve_installer_path(
        self,
        installer_root: Path,
        project: Project,
        version: str | None,
        revision: int | None,
    ) -> Path:
        """
        Resolve a pasta de saída do Setup.

        Quando version e revision são informados,
        utiliza a estrutura:

            {installer_root}
                └── {version}.{revision}
                    └── Cliente / Server

        Quando não são informados, mantém o comportamento
        anterior utilizando diretamente installer_root.
        """

        #
        # Mantém compatibilidade com o comportamento antigo.
        #

        if version is None and revision is None:
            return installer_root

        #
        # A versão é obrigatória quando a revisão
        # for utilizada.
        #

        if version is None or not str(version).strip():
            raise ValueError(
                "A versão do Setup não foi informada."
            )

        if revision is None:
            raise ValueError(
                "A revisão do Setup não foi informada."
            )

        if revision < 0:
            raise ValueError(
                "A revisão do Setup não pode ser negativa."
            )

        #
        # Monta a versão completa.
        #

        version_value = (
            str(version).strip()
        )

        version_folder = (
            f"{version_value}.{revision}"
        )

        #
        # Resolve o tipo do projeto.
        #

        project_type_folder = (
            self.__resolve_project_type_folder(
                project.type,
            )
        )

        return (
            installer_root
            / version_folder
            / project_type_folder
        )

    def __resolve_project_type_folder(
        self,
        project_type: ProjectType,
    ) -> str:
        """
        Converte o tipo do projeto para o nome
        da pasta de saída.
        """

        if project_type == ProjectType.CLIENT:
            return "Cliente"

        if project_type == ProjectType.SERVER:
            return "Server"

        raise ValueError(
            "O tipo do projeto não é suportado "
            "para geração do Setup: "
            f"{project_type}"
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
    def __resolve_optional_project_path(
        self,
        value: str | None,
        project_root: Path,
    ) -> Path | None:
        """
        Resolve um caminho opcional configurado no Project.

        Caminhos absolutos são respeitados.

        Caminhos relativos são considerados relativos
        à raiz física do projeto.

        Quando o valor não estiver configurado,
        retorna None.
        """

        if value is None:
            return None

        if not value.strip():
            return None

        path = Path(
            value.strip(),
        )

        if path.is_absolute():
            return path

        return (
            project_root / path
        )

    def __resolve_optional_workspace_path(
        self,
        value: str | None,
        workspace_root: Path,
    ) -> Path | None:
        """
        Resolve um caminho opcional configurado no Project
        relativo à raiz física do workspace.

        Caminhos absolutos são respeitados.

        Caminhos relativos são considerados relativos
        à raiz física do workspace.

        Quando o valor não estiver configurado,
        retorna None.
        """

        if value is None:
            return None

        if not value.strip():
            return None

        path = Path(
            value.strip(),
        )

        if path.is_absolute():
            return path

        return (
            workspace_root / path
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