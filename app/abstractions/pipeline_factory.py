"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_factory.py
Descrição : Contrato responsável pela criação de Pipelines.
--------------------------------------------------------------------
"""

from abc import ABC
from abc import abstractmethod

from app.models.pipeline.pipeline import Pipeline
from app.models.project.project import Project


class PipelineFactory(ABC):
    """
    Responsável por criar uma Pipeline para um projeto.
    """

    @abstractmethod
    def create(
        self,
        project: Project,
    ) -> Pipeline:
        """
        Cria uma Pipeline.
        """
        raise NotImplementedError