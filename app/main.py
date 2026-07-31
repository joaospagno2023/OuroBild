"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : main.py
Descrição : Ponto de entrada da aplicação.
--------------------------------------------------------------------
"""

from app.bootstrap import Bootstrap

bootstrap = Bootstrap()

app = bootstrap.create_app()