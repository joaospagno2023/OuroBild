"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_execution_lock.py
Descrição : Controle de concorrência das execuções de Publish.
--------------------------------------------------------------------
"""

from threading import Lock


class PublishExecutionLock:
    """
    Controla a execução concorrente de Publish.

    Permite somente uma execução de Publish
    por vez dentro da instância da aplicação.
    """

    def __init__(
        self,
    ) -> None:

        self.__lock = Lock()

    def try_acquire(
        self,
    ) -> bool:
        """
        Tenta adquirir o Lock.

        Returns:
            True quando o Lock foi adquirido.
            False quando já existe uma execução.
        """

        return self.__lock.acquire(
            blocking=False,
        )

    def release(
        self,
    ) -> None:
        """
        Libera o Lock da execução atual.
        """

        self.__lock.release()