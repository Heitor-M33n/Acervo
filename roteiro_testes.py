from datetime import date, timedelta

from rich.console import Console

import models
import core

o1 = models.Obra('1984', 'George Oell', 1949, 'Distopia/Ficção Científica', 5)
o2 = models.Obra('Dom Quixote', 'Miguel de Cervantes', 1605, 'Romance/Literatura Clássica', 10)
o3 = models.Obra('O Senhor do Anéis', 'J.R.R Tolkien', 1954, 'Fantasia Épica', 5)

console = Console()
acervo = core.Acervo()

acervo.adicionar(o1)
acervo.adicionar(o2)
acervo.adicionar(o3)

u1 = models.Usuario('Heitor', 'aaa@gmail.com')
emp1 = acervo.emprestar(o1, u1)
print(acervo.estoque)

acervo.devolver(emp1, data_dev=date(2025, 7, 24))
print(acervo.estoque)
print(u1.debitos)

console.print(acervo._relatorio_builder('inv'))
console.print(acervo._relatorio_builder('user_deb', u1))
console.print(acervo._relatorio_builder('user_mov', u1))
