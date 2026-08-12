"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_metadata_service.py
Descrição : Serviço responsável pelo gerenciamento da metadata
            dos projetos.
--------------------------------------------------------------------
"""

from datetime import datetime
from pathlib import Path

from app.abstractions.project_metadata_repository import (
    ProjectMetadataRepository,
)

from app.models.project.project_metadata import (
    ProjectMetadata,
)

from app.services.hash_service import (
    HashService,
)


class ProjectMetadataService:
    """
    Serviço responsável por gerenciar
    a metadata dos projetos.
    """

    def __init__(
        self,
        repository: ProjectMetadataRepository,
        hash_service: HashService,
    ) -> None:
        """
        Inicializa o serviço.
        """

        self.__repository = repository
        self.__hash_service = hash_service

    def load(
        self,
        project_id: str,
    ) -> ProjectMetadata | None:
        """
        Carrega a metadata de um projeto.
        """

        return self.__repository.load(
            project_id,
        )

    def save(
        self,
        metadata: ProjectMetadata,
    ) -> None:
        """
        Salva a metadata de um projeto.
        """

        self.__repository.save(
            metadata,
        )

    def exists(
        self,
        project_id: str,
    ) -> bool:
        """
        Verifica se existe metadata.
        """

        return self.__repository.exists(
            project_id,
        )

    def delete(
        self,
        project_id: str,
    ) -> None:
        """
        Remove a metadata.
        """

        self.__repository.delete(
            project_id,
        )

    def update_from_analysis(
        self,
        project_id: str,
        project_file: Path,
    ) -> ProjectMetadata:
        """
        Atualiza a metadata após uma análise.

        Quando já existir metadata, preserva o
        restore_hash existente.
        """

        metadata = self.load(
            project_id,
        )

        current_hash = (
            self.__hash_service.calculate_file_hash(
                project_file,
            )
        )

        project_last_write = (
            datetime.fromtimestamp(
                project_file.stat().st_mtime,
            )
        )

        #
        # Se ainda não existe metadata,
        # cria uma nova.
        #

        if metadata is None:

            metadata = ProjectMetadata(
                project_id=project_id,
                project_hash=current_hash,
                project_last_write=(
                    project_last_write
                ),
                last_analysis=datetime.now(),
            )

        #
        # Se já existe, atualiza somente os
        # dados relacionados à análise.
        #

        else:

            metadata.project_hash = (
                current_hash
            )

            metadata.project_last_write = (
                project_last_write
            )

            metadata.last_analysis = (
                datetime.now()
            )

        self.__repository.save(
            metadata,
        )

        return metadata

    def is_restore_required(
        self,
        project_id: str,
        project_file: Path,
    ) -> bool:
        """
        Verifica se o projeto precisa executar Restore.

        Retorna True quando:

        - a metadata não existe;
        - o restore_hash não existe;
        - o hash atual do projeto é diferente
          do hash registrado no último Restore.

        Retorna False somente quando existe um
        restore_hash válido e ele corresponde ao
        hash atual do arquivo do projeto.
        """

        metadata = self.load(
            project_id,
        )

        #
        # Sem metadata não temos como comprovar
        # que o projeto já passou por Restore.
        #

        if metadata is None:
            return True

        current_hash = (
            self.__hash_service.calculate_file_hash(
                project_file,
            )
        )

        #
        # Sem restore_hash não podemos considerar
        # o Restore válido.
        #

        if not metadata.restore_hash:
            return True

        #
        # Restore somente pode ser ignorado quando
        # o hash atual é exatamente igual ao hash
        # registrado após o último Restore bem-sucedido.
        #

        return (
            current_hash
            != metadata.restore_hash
        )

    def update_restore_hash(
        self,
        project_id: str,
        project_file: Path,
    ) -> None:
        """
        Atualiza o hash do projeto após um Restore
        executado com sucesso.

        O hash somente deve ser atualizado depois
        que o Restore terminar com sucesso.

        Se a metadata ainda não existir, ela será
        criada neste momento.
        """

        metadata = self.load(
            project_id,
        )

        current_hash = (
            self.__hash_service.calculate_file_hash(
                project_file,
            )
        )

        project_last_write = (
            datetime.fromtimestamp(
                project_file.stat().st_mtime,
            )
        )

        #
        # PRIMEIRO RESTORE
        #
        # Ainda não existe metadata.
        #

        if metadata is None:

            metadata = ProjectMetadata(
                project_id=project_id,
                project_hash=current_hash,
                project_last_write=(
                    project_last_write
                ),
                last_analysis=None,
            )

        #
        # RESTORE POSTERIOR
        #
        # A metadata já existe.
        #

        else:

            metadata.project_hash = (
                current_hash
            )

            metadata.project_last_write = (
                project_last_write
            )

        #
        # Este é o ponto fundamental:
        #
        # O restore_hash somente é atualizado
        # depois que o Restore terminou com sucesso.
        #

        metadata.restore_hash = (
            current_hash
        )

        #
        # Persiste a metadata.
        #

        self.save(
            metadata,
        )