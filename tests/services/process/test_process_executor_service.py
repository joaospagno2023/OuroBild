"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_process_executor_service.py
Descrição : Testes do ProcessExecutorService.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.models.process.process_status import (
    ProcessStatus,
)
from app.services.process.process_executor_service_impl import (
    ProcessExecutorServiceImpl,
)


def test_should_execute_dotnet_version():
    """
    Deve executar o comando
    dotnet --version.
    """

    #
    # Arrange
    #

    service = ProcessExecutorServiceImpl()

    #
    # Act
    #

    result = service.execute(
        executable="dotnet",
        arguments=[
            "--version",
        ],
        working_directory=Path.cwd(),
    )

    #
    # Assert
    #

    assert result.status == ProcessStatus.SUCCESS

    assert result.exit_code == 0

    assert result.stdout.strip() != ""