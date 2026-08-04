"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : recommendation.py
Descrição : Representa uma recomendação gerada durante a análise.
--------------------------------------------------------------------
"""

from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class Recommendation:
    """
    Representa uma recomendação de melhoria
    para um projeto.
    """

    code: str

    title: str

    description: str