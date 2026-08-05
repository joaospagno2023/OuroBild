"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : dataclass_json_serializer.py
Descrição : Serializador genérico para Dataclasses.
--------------------------------------------------------------------
"""

import json

from dataclasses import asdict
from pathlib import Path
from typing import Any


class DataclassJsonSerializer:
    """
    Responsável por serializar
    Dataclasses para JSON.
    """

    def save(
        self,
        file: Path,
        obj: Any,
    ) -> None:
        """
        Salva uma Dataclass em JSON.
        """

        file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            file,
            "w",
            encoding="utf-8",
        ) as fp:

            json.dump(

                asdict(
                    obj,
                ),

                fp,

                indent=4,

                ensure_ascii=False,

                default=str,
            )

    def load(
        self,
        file: Path,
    ) -> dict:
        """
        Carrega um JSON.
        """

        with open(
            file,
            "r",
            encoding="utf-8",
        ) as fp:

            return json.load(
                fp,
            )