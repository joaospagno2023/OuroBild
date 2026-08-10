"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : solution_locator_service.py
Descrição : Responsável por localizar automaticamente a Solution
             correspondente ao projeto.
--------------------------------------------------------------------
"""

from pathlib import Path


class SolutionLocatorService:
    """
    Localiza automaticamente a Solution (.sln) que contém um projeto.
    """

    def find_solution(
        self,
        project_file: Path,
    ) -> Path | None:
        """
        Localiza a Solution correspondente ao projeto.
        """
       

        workspace = self.__find_workspace_root(
            project_file,
        )
        

        if workspace is None:
            return None

        solutions = sorted(
            workspace.glob("*.sln"),
        )

        if not solutions:
            return None

        #
        # Apenas uma Solution
        #

        if len(solutions) == 1:
            return solutions[0]

        #
        # Várias Solutions
        #

        for solution in solutions:

            if self.__contains_project(
                solution,
                project_file,
            ):

                return solution

        return None

    def __find_workspace_root(
        self,
        project_file: Path,
    ) -> Path | None:
        """
        Localiza a pasta raiz do Workspace.

        Exemplo:

        OuroNet
            |
            +-- OuroNet 10.4.7.sln
            |
            +-- 02-Source
                  |
                  +-- 01-Client
        """

        current = project_file.parent

        while True:

            #
            # Encontrou a pasta 02-Source
            #

            if current.name.lower() == "02-source":

                #
                # A Solution fica um nível acima
                #

                return current.parent

            #
            # Chegou na raiz
            #

            if current.parent == current:
                return None

            current = current.parent

    def __contains_project(
        self,
        solution_file: Path,
        project_file: Path,
    ) -> bool:
        """
        Verifica se a Solution contém o projeto.
        """

        try:

            relative_project = project_file.relative_to(
                solution_file.parent,
            )

        except ValueError:

            return False

        project_reference = (
            str(relative_project)
            .replace("/", "\\")
            .lower()
        )

        try:

            content = solution_file.read_text(
                encoding="utf-8",
                errors="ignore",
            ).lower()

        except OSError:

            return False

        return project_reference in content