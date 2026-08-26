"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : temporary_solution_service.py
Descrição : Cria uma Solution temporária para geração de Setup.
--------------------------------------------------------------------
"""

import re

from pathlib import Path


class TemporarySolutionService:
    """
    Cria uma cópia temporária da Solution para execução do Setup.

    A Solution original nunca é alterada.

    A Solution temporária:
    - mantém os GUIDs originais;
    - mantém os nomes dos projetos;
    - mantém as configurações da Solution;
    - utiliza caminhos absolutos para os projetos existentes;
    - aponta o projeto Setup para o VDPROJ temporário.
    """

    #
    # O lookahead (?=\r?$) substitui o antigo "$" simples.
    #
    # O "$" do modo MULTILINE só reconhece o fim de linha
    # imediatamente antes de um "\n". Em arquivos .sln com
    # quebra de linha "\r\n" (padrão do Windows), sobra um
    # "\r" entre o fechamento da GUID e o "$", e a linha
    # inteira deixa de casar com o padrão — a substituição
    # do caminho do projeto simplesmente não acontece.
    #

    _PROJECT_PATTERN = re.compile(
        r'^(Project\("[^"]+"\)\s*=\s*"[^"]+"\s*,\s*)"([^"]+)"(\s*,\s*"\{[^"]+\}")(?=\r?$)',
        re.MULTILINE,
    )

    #
    # Remove o GlobalSection(SourceCodeControl) inteiro.
    #
    # Solutions antigas do TFS/VSS costumam conter esse bloco
    # com bindings apontando para um provider fictício ("SAK").
    #
    # Se esse bloco não for removido, o devenv.com recusa a
    # geração do Setup com o erro:
    #
    #   "Could not find the 'SAK' source control provider
    #    set by the 'SccProvider' property."
    #

    _SOURCE_CONTROL_SECTION_PATTERN = re.compile(
        r'[ \t]*GlobalSection\(SourceCodeControl\)'
        r'.*?EndGlobalSection\r?\n?',
        re.DOTALL,
    )

    #
    # Remove qualquer linha remanescente com bindings Scc,
    # inclusive as que aparecem dentro de blocos de projeto
    # (ProjectSection) em solutions mais antigas.
    #

    _SCC_LINE_PATTERN = re.compile(
        r'^[ \t]*Scc[A-Za-z0-9]*\s*=.*\r?\n?',
        re.MULTILINE,
    )

    #
    # Propriedades de Source Control que aparecem
    # DENTRO de arquivos .vdproj individuais.
    #
    # Além do GlobalSection(SourceCodeControl) do .sln,
    # cada .vdproj referenciado pela Solution carrega seus
    # próprios bindings ("SccProvider" = "8:SAK" etc.).
    #
    # O devenv.com falha ao carregar QUALQUER projeto da
    # Solution com esse binding, mesmo quando construímos
    # apenas um projeto específico via /Project — por isso
    # é necessário limpar também os outros .vdproj
    # referenciados, não somente o projeto alvo.
    #

    _VDPROJ_SCC_PROPERTIES = (
        '"SccProjectName"',
        '"SccLocalPath"',
        '"SccAuxPath"',
        '"SccProvider"',
    )

    #
    # Mesmas propriedades de Source Control, só que no
    # formato XML usado por projetos MSBuild (.csproj,
    # .vbproj, .vcxproj) vinculados ao TFS/VSS clássico:
    #
    #   <SccProjectName>SAK</SccProjectName>
    #   <SccLocalPath>SAK</SccLocalPath>
    #   <SccAuxPath>SAK</SccAuxPath>
    #   <SccProvider>SAK</SccProvider>
    #
    # O devenv.com recusa carregar QUALQUER projeto da
    # Solution — de qualquer tipo — que ainda tenha esses
    # bindings apontando para o provider fictício "SAK".
    #

    _MSBUILD_SCC_LINE_PATTERN = re.compile(
        r'^[ \t]*<Scc[A-Za-z0-9]*>.*</Scc[A-Za-z0-9]*>\s*\r?\n?',
        re.MULTILINE,
    )

    _MSBUILD_PROJECT_SUFFIXES = (
        ".csproj",
        ".vbproj",
        ".vcxproj",
        ".fsproj",
    )

    def create(
        self,
        solution_path: Path,
        publish_path: Path,
        original_setup_project_path: Path,
        temporary_setup_project_path: Path,
    ) -> Path:
        """
        Cria uma Solution temporária.

        Parameters
        ----------
        solution_path:
            Caminho da Solution original.

        publish_path:
            Diretório onde a Solution temporária será criada.

        original_setup_project_path:
            Caminho do VDPROJ original.

        temporary_setup_project_path:
            Caminho do VDPROJ temporário.

        Returns
        -------
        Path
            Caminho da Solution temporária.
        """

        if solution_path is None:
            raise ValueError(
                "SolutionPath não foi informado."
            )

        if publish_path is None:
            raise ValueError(
                "PublishPath não foi informado."
            )

        if original_setup_project_path is None:
            raise ValueError(
                "OriginalSetupProjectPath "
                "não foi informado."
            )

        if temporary_setup_project_path is None:
            raise ValueError(
                "TemporarySetupProjectPath "
                "não foi informado."
            )

        solution_path = Path(
            solution_path,
        )

        publish_path = Path(
            publish_path,
        )

        original_setup_project_path = (
            Path(
                original_setup_project_path,
            )
        )

        temporary_setup_project_path = (
            Path(
                temporary_setup_project_path,
            )
        )

        if not solution_path.exists():
            raise FileNotFoundError(
                "Solution original não encontrada: "
                f"{solution_path}"
            )

        if not solution_path.is_file():
            raise ValueError(
                "Solution original não é um arquivo: "
                f"{solution_path}"
            )

        if not original_setup_project_path.exists():
            raise FileNotFoundError(
                "Projeto Setup original não encontrado: "
                f"{original_setup_project_path}"
            )

        if not temporary_setup_project_path.exists():
            raise FileNotFoundError(
                "Projeto Setup temporário não encontrado: "
                f"{temporary_setup_project_path}"
            )

        publish_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        content = self.__read_solution(
            solution_path,
        )

        #
        # Normaliza as quebras de linha para "\n".
        #
        # Arquivos .sln do Visual Studio usam CRLF ("\r\n").
        # Os regex de conversão de paths e remoção de bindings
        # Scc usam o âncora "$" em modo MULTILINE, que só
        # reconhece "\n" como fim de linha — com CRLF, o "\r"
        # remanescente impede o casamento e nenhuma substituição
        # é aplicada (os paths relativos ficam intactos, e o
        # devenv.com passa a resolvê-los a partir do diretório
        # errado, causando "Could not find a part of the path").
        #

        content = content.replace(
            "\r\n",
            "\n",
        )

        content = self.__strip_source_control(
            content,
        )

        content = self.__convert_project_paths(
            content=content,
            solution_directory=(
                solution_path.parent
            ),
            original_setup_project_path=(
                original_setup_project_path
            ),
            temporary_setup_project_path=(
                temporary_setup_project_path
            ),
            publish_path=publish_path,
        )

        #
        # Restaura o padrão CRLF ao gravar, mantendo o
        # arquivo compatível com o formato esperado pelo
        # Visual Studio.
        #

        content = content.replace(
            "\n",
            "\r\n",
        )

        temporary_solution_path = (
            publish_path
            / self.__build_solution_name(
                solution_path,
            )
        )

        self.__write_solution(
            temporary_solution_path,
            content,
        )

        return temporary_solution_path

    @staticmethod
    def __read_solution(
        solution_path: Path,
    ) -> str:
        """
        Lê a Solution original.
        """

        data = solution_path.read_bytes()

        if data.startswith(
            b"\xef\xbb\xbf"
        ):
            return data.decode(
                "utf-8-sig",
            )

        try:
            return data.decode(
                "utf-8",
            )
        except UnicodeDecodeError:
            return data.decode(
                "cp1252",
            )

    @classmethod
    def __strip_source_control(
        cls,
        content: str,
    ) -> str:
        """
        Remove os bindings de source control (Scc*) da Solution.

        A Solution temporária não deve carregar bindings
        de source control, pois eles não fazem sentido fora
        do Workspace original e podem apontar para provedores
        que não estão instalados (ex.: "SAK").
        """

        content = cls._SOURCE_CONTROL_SECTION_PATTERN.sub(
            "",
            content,
        )

        content = cls._SCC_LINE_PATTERN.sub(
            "",
            content,
        )

        return content

    @classmethod
    def __convert_project_paths(
        cls,
        content: str,
        solution_directory: Path,
        original_setup_project_path: Path,
        temporary_setup_project_path: Path,
        publish_path: Path,
    ) -> str:
        """
        Converte os caminhos dos projetos da Solution.

        Todos os projetos passam a utilizar caminhos absolutos.

        O projeto Setup alvo aponta para o VDPROJ temporário.

        Os demais projetos .vdproj referenciados pela Solution
        apontam para cópias temporárias, com os bindings Scc
        removidos, para que o devenv.com consiga carregar a
        Solution inteira sem exigir o provider "SAK".
        """

        original_setup_project_path = (
            original_setup_project_path
            .resolve()
        )

        temporary_setup_project_path = (
            temporary_setup_project_path
            .resolve()
        )

        def replace_project(
            match: re.Match,
        ) -> str:
            prefix = match.group(1)
            project_path_text = match.group(2)
            suffix = match.group(3)

            if not project_path_text:
                return match.group(0)

            #
            # Solution folders não possuem caminho de
            # projeto real e não entram neste processamento.
            #

            project_path = Path(
                project_path_text,
            )

            if project_path.is_absolute():
                resolved_project_path = (
                    project_path.resolve()
                )
            else:
                resolved_project_path = (
                    solution_directory
                    / project_path
                ).resolve()

            #
            # Se for o Setup alvo, apontamos
            # para o Setup temporário já preparado.
            #

            if cls.__same_path(
                resolved_project_path,
                original_setup_project_path,
            ):
                target_path = (
                    temporary_setup_project_path
                )

            elif resolved_project_path.suffix.lower() == ".vdproj":
                #
                # Outro projeto de Setup (não é o alvo):
                # geramos uma cópia temporária sem Scc,
                # para que o devenv não recuse a Solution
                # inteira por causa do provider "SAK".
                #

                target_path = (
                    cls.__prepare_other_vdproj(
                        original_vdproj_path=(
                            resolved_project_path
                        ),
                        publish_path=publish_path,
                    )
                )

            elif (
                resolved_project_path.suffix.lower()
                in cls._MSBUILD_PROJECT_SUFFIXES
            ):
                #
                # Projeto MSBuild (.csproj/.vbproj/etc.):
                # mesma lógica, mas removendo os bindings
                # Scc em formato XML.
                #

                target_path = (
                    cls.__prepare_other_msbuild_project(
                        original_project_path=(
                            resolved_project_path
                        ),
                        publish_path=publish_path,
                    )
                )

            else:
                #
                # Demais tipos de projeto (.csproj etc.)
                # continuam sendo os projetos originais.
                #

                target_path = (
                    resolved_project_path
                )

            return (
                prefix
                + '"'
                + cls.__solution_path(
                    target_path,
                )
                + '"'
                + suffix
            )

        return cls._PROJECT_PATTERN.sub(
            replace_project,
            content,
        )

    @classmethod
    def __prepare_other_vdproj(
        cls,
        original_vdproj_path: Path,
        publish_path: Path,
    ) -> Path:
        """
        Cria, em publish_path, uma cópia do .vdproj informado
        com os bindings Scc removidos.

        O .vdproj original nunca é alterado.

        Se o arquivo original não existir (referência quebrada
        na Solution) ou não puder ser lido, devolve o caminho
        original sem modificação — quem for chamar o devenv
        vai reportar o erro real nesse caso.
        """

        if not original_vdproj_path.exists():
            return original_vdproj_path

        try:
            data = original_vdproj_path.read_bytes()

            if data.startswith(b"\xef\xbb\xbf"):
                text = data.decode("utf-8-sig")
            else:
                try:
                    text = data.decode("utf-8")
                except UnicodeDecodeError:
                    text = data.decode("cp1252")

        except OSError:
            return original_vdproj_path

        lines = text.splitlines(keepends=True)

        cleaned_text = "".join(
            line
            for line in lines
            if not line.lstrip().startswith(
                cls._VDPROJ_SCC_PROPERTIES,
            )
        )

        #
        # Prefixo para não colidir com outros arquivos
        # já existentes em publish_path (ex.: o próprio
        # Setup alvo).
        #

        temp_vdproj_path = (
            publish_path
            / f"{original_vdproj_path.stem}.OuroBuildRef.vdproj"
        )

        temp_vdproj_path.write_text(
            cleaned_text,
            encoding="utf-8",
            newline="",
        )

        return temp_vdproj_path

    @classmethod
    def __prepare_other_msbuild_project(
        cls,
        original_project_path: Path,
        publish_path: Path,
    ) -> Path:
        """
        Cria, em publish_path, uma cópia do projeto MSBuild
        informado (.csproj/.vbproj/.vcxproj/.fsproj) com os
        bindings Scc em formato XML removidos.

        O projeto original nunca é alterado.

        Se o arquivo original não existir ou não puder ser
        lido, devolve o caminho original sem modificação.
        """

        if not original_project_path.exists():
            return original_project_path

        try:
            data = original_project_path.read_bytes()

            if data.startswith(b"\xef\xbb\xbf"):
                text = data.decode("utf-8-sig")
            else:
                try:
                    text = data.decode("utf-8")
                except UnicodeDecodeError:
                    text = data.decode("cp1252")

        except OSError:
            return original_project_path

        cleaned_text = cls._MSBUILD_SCC_LINE_PATTERN.sub(
            "",
            text,
        )

        if cleaned_text == text:
            #
            # Nada foi alterado: não há necessidade de
            # criar uma cópia, o projeto original já
            # pode ser usado diretamente.
            #

            return original_project_path

        temp_project_path = (
            publish_path
            / (
                f"{original_project_path.stem}"
                ".OuroBuildRef"
                f"{original_project_path.suffix}"
            )
        )

        temp_project_path.write_text(
            cleaned_text,
            encoding="utf-8",
            newline="",
        )

        return temp_project_path

    @staticmethod
    def __same_path(
        first: Path,
        second: Path,
    ) -> bool:
        """
        Compara dois caminhos de forma segura.
        """

        return (
            first.resolve()
            == second.resolve()
        )

    @staticmethod
    def __solution_path(
        path: Path,
    ) -> str:
        """
        Converte um caminho para o formato aceito
        pelo arquivo .sln.
        """

        return str(
            path.resolve()
        ).replace(
            "\\",
            "/",
        )

    @staticmethod
    def __build_solution_name(
        solution_path: Path,
    ) -> str:
        """
        Gera o nome da Solution temporária.
        """

        return (
            f"{solution_path.stem}"
            ".OuroBuild.sln"
        )

    @staticmethod
    def __write_solution(
        solution_path: Path,
        content: str,
    ) -> None:
        """
        Grava a Solution temporária.
        """

        solution_path.write_text(
            content,
            encoding="utf-8",
            newline="",
        )