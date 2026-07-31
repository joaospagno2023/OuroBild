from app.models.project.project import Project
from app.use_cases.get_projects_use_case import GetProjectsUseCase


class FakeProjectRepository:
    def get_all(self) -> list[Project]:
        return [
            Project(
                id="link-pagamento",
                name="Projeto Teste",
                description="Projeto para teste",
                project_path="Projeto.csproj",
                aip_path="Projeto.aip",
                publish_path="publish",
                output_msi="Projeto.msi",
                network_path="\\\\servidor\\instaladores",
                configuration="Release",
                platform="AnyCPU",
                enabled=True,
            )
        ]


def test_execute_returns_projects():
    repository = FakeProjectRepository()
    use_case = GetProjectsUseCase(repository)

    projects = use_case.execute()

    assert len(projects) == 1
    assert projects[0].name == "Projeto Teste"
    assert projects[0].enabled is True