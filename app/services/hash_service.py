"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : hash_service.py
Descrição : Serviço responsável pelo cálculo de hash de arquivos.
--------------------------------------------------------------------
"""

import hashlib

from pathlib import Path


class HashService:
    """
    Responsável pelo cálculo de hash SHA256
    de arquivos.
    """

    def calculate_file_hash(
        self,
        file: Path,
    ) -> str:
        """
        Calcula o hash SHA256 de um arquivo.
        """

        sha256 = hashlib.sha256()

        with file.open(
            "rb",
        ) as fp:

            while True:

                chunk = fp.read(
                    8192,
                )

                if not chunk:

                    break

                sha256.update(
                    chunk,
                )

        return sha256.hexdigest()