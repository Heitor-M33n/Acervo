from datetime import date
from datetime import timedelta

from rich.table import Table

from models import Emprestimo
from models import Obra
from models import Usuario

class Acervo:
    """Acervo, realiza e manipula empréstimos, armazena estoque de obras                     

    Armazena as obras em um dicionário em que as keys são seus ids, realiza a manipulação total dos empréstimos
    E possui uma classe interna responsável por criar relatórios
    
    Attributes:
        estoque (dict): dicionário no formato {obra.titulo: obra.quantidade}
        emprestimos_ativos (list): lista de todos empréstimos em vigor
    """

    __slots__ = ['estoque', 'emprestimos_ativos']

    def _relatorio_builder(self):
        pass

    class _RelatorioBuilder:
        pass

    def __init__(self) -> None:
        """Inicializa Acervo
        """
        self.estoque = {'Obra': 'qtd_disponível'}  
        self.emprestimos_ativos = []

    def __iadd__(self, obra: Obra):
        """Função do operador +=, adiciona uma obra no estoque, caso já esteja nele, +1 quantidade
        
        Args:
            obra (Obra): obra que está sendo incrementada ao estoque
        """
        if obra in self.estoque:
            obra.quantidade += 1
        else:
            self.estoque[obra.titulo] = obra.quantidade

        return self

    def __isub__(self, obra: Obra):
        """Função do operador -=, -1 quantidade de uma obra, caso se torne 0, remove completamente do estoque
        
        Args:
            obra (Obra): Obra que está sendo decrementada do estoque
        """
        if obra in self.estoque:
            obra.quantidade -= 1
        else:
            pass

        if obra.quantidade <= 0:
            self.estoque.pop(obra.titulo, None)

        return self

    def adicionar(self, obra: Obra) -> None:
        """Interface explícita para +=
        
        Args:
            obra (Obra): Obra que está sendo incrementada ao estoque
        """
        self += obra

    def remover(self, obra: Obra) -> None:
        """Interface explícita para -=
        
        Args:
            obra (Obra): Obra que está sendo decrementada do estoque
        """
        self -= obra

    def emprestar(self, obra: Obra, usuario: Usuario, dias: int = 7) -> Emprestimo:
        """Cria um empréstimo com uma data de devolução prevista em 7 dias
        
        Como uma obra foi emprestada, decrementa 1 do estoque

        Args:
            obra (Obra): Obra que será emprestada
            usuario (Usuario): Usuario realizando o empréstimo
            dias (int): Dias até a devolução, por padrão, 7

        Raises:
            ValueError: Ocorre caso a obra não esteja em estoque    
        """
        if obra.disponivel(self.estoque):
            self.remover(obra)
            emp = Emprestimo(obra, usuario, date.today() + timedelta(days=dias))
            self.emprestimos_ativos.append(emp)
            return emp
        else:
            raise ValueError

    def devolver(self, emprestimo: Emprestimo, data_dev: date = date.today()) -> None:
        """Finaliza um empréstimo, retornando a obra ao estoque
        
        Args:
            emprestimo (Emprestimo): Empréstimo realizado
            data_dev (date): Data em que a obra foi devolvida ( por padrão o dia atual )
        """
        if emprestimo.dias_atraso():
            self.multar()

        self.adicionar(emprestimo.obra)
        self.emprestimos_ativos.pop(emprestimo)
        emprestimo.marcar_devolucao()
    
    def renovar(self, emprestimo: Emprestimo, dias_extras: timedelta = timedelta(days=7)) -> None:
        """Adia a data de devolução de um empréstimo
        
        Args:
            emprestimo (Emprestimo): Empréstimo realizado
            dias_extras (timedelta): Dias adicionados
        """
        if emprestimo.dias_atraso() > dias_extras:
            return
            #Atraso tão grande que mesmo renovando ainda está atrasado, ainda estou vendo o que vou fazer

        if emprestimo.dias_atraso():
            self.multar(emprestimo)

        emprestimo.data_prev_devol += dias_extras

    def valor_multa(self, emprestimo: Emprestimo) -> float:
        """Calcula a multa sobre o atraso entre a data_prev_dev e a data_ref

        A multa é de R$ 1,00 por dia de atraso
        
        Args:
            emprestimo (Emprestimo): Empréstimo realizado
            data_ref (date): Data de referência ( por padrão o dia atual )

        Returns:
            float: Retorna o valor da multa em reais
        """
        return float(emprestimo.dias_atraso())

    def multar(self, emprestimo: Emprestimo):
        pass

    def _valida_obra(self, obra: Obra) -> bool:
        """Valida se uma obra é de fato da classe Obra
        
        Args:
            obra (Obra): Obra que está sendo verificada
            
        Raises:
            TypeError: Caso a obra não seja da classe Obra
            """
        if not isinstance(obra, Obra):
            raise TypeError