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

    class _RelatorioBuilder:
        def relatorio_inventario(self, acervo) -> Table:
            """Cria uma tabela do inventário de um Acervo.
            
            Args:
                acervo (Acervo): Acervo do respectivo inventário
            
            Returns:
                Table: Retorna a tabela de obras.
            """
            tabela = Table(title='Inventário do Acervo')

            tabela.add_column('Obra', justify='center')
            tabela.add_column('Quantidade', justify='left')

            estoque_ordenado = dict(sorted(acervo.estoque.items(), key=lambda item: item[1]))

            for obra, qnt in estoque_ordenado.items():
                tabela.add_row(obra, str(qnt))

            return tabela
        
        def relatorio_debitos_usuario(self, user: Usuario) -> Table:
            """Cria uma tabela de débitos de um usuário específico.
            
            Args:
                user (Usuario): Usuário responsável pelos débitos
            
            Returns:
                Table: Retorna a tabela de débitos.
            """
            tabela = Table(title=f'Débitos de {user}')

            tabela.add_column('Motivo', justify='center')
            tabela.add_column('Quantia', justify='left')

            if not user.debitos:
                tabela.add_row('N/A', 'N/A')
                return tabela

            for mot, qnt in user.debitos.items():
                tabela.add_row(mot, qnt)

            return tabela
        
        def relatorio_movimentacoes_usuario(self, user: Usuario) -> Table:
            """Cria uma tabela de movimentações de um usuário específico.
            
            Args:
                user (Usuario): Usuário responsável pelas movimentações
                
            Returns:
                Table: Retorna a tabela de movimentações.
            """
            tabela = Table(title=f'Movimentações de {user}')

            tabela.add_column('Obra', justify='center')
            tabela.add_column('Estado', justify='center')
            tabela.add_column('Data prevista de devolução', justify='right')
            tabela.add_column('Data de devolução', justify='right')

            def estado(emprestimo: Emprestimo) -> str:
                """Função interna para verificar se o empréstimo foi devolvido e retornar uma string coerente.
                
                Args:
                    emprestimo (Emprestimo): emprestimo que está sendo verificado.
                    
                Returns:
                    str: retorna "Devolvido", "Atrasado ( x dias )" ou "Em dia", a depender da verificação.
                """
                if emprestimo.data_dev_real:
                    return 'Devolvido'
                elif emprestimo.dias_atraso():
                    return f'Atrasado ( {emprestimo.dias_atraso()} dias )'
                return 'Em dia'

            def data_dev(emprestimo: Emprestimo) -> str:
                """Função interna para verificar se o empréstimo foi devolvido e retornar uma string coerente.
                
                Args:
                    emprestimo (Emprestimo): emprestimo que está sendo verificado.
                    
                Returns:
                    str: retorna a data, caso esteja em andamento, retorna "...".
                """
                if emprestimo.data_dev_real:
                    return emprestimo.data_dev_real.strftime('%d/%m/%y')
                return '...'

            if not user.emprestimos:
                tabela.add_row('N/A', 'N/A', 'N/A', 'N/A')
                return tabela

            emp: Emprestimo
            for emp in user.emprestimos:
                tabela.add_row(emp.obra.titulo, estado(emp), str(emp.data_prev_devol.strftime('%d/%m/%y')), data_dev(emp))

            return tabela

        def relatorio_historico_users(self) -> Table:
            pass

        def relatorio_emprestimos_ativos(self, acervo) -> Table:
            pass

        def relatorio_historico_emprestimos(self) -> Table:
            pass

        def relatorio_completo(self, acervo, user: Usuario) -> Table:
            pass

    def _relatorio_builder(self, type: str = 'inv', user: Usuario = None) -> Table:
        """Faz um relatório baseado no tipo solicitado.
        
        ('inv', 'user_deb', 'user_mov')
        
        Args: 
            type (str): tipo de relatório, ver tupla acima.
            user (Usuario): usuário referente ao relatório, quando necessário.
            
        Returns:
            Table: retorna o relatório
        """
        rel_builder = self._RelatorioBuilder()
        match type:
            case 'inv':
                rel = rel_builder.relatorio_inventario(self)
            case 'user_deb':
                rel = rel_builder.relatorio_debitos_usuario(user)
            case 'user_mov':
                rel = rel_builder.relatorio_movimentacoes_usuario(user)
            case 'user_hist':
                rel = rel_builder.relatorio_historico_users() #Para fazer
            case 'emp_ativos':
                rel = rel_builder.relatorio_emprestimos_ativos(self) #Para fazer
            case 'emp_hist':
                rel = rel_builder.relatorio_historico_emprestimos() #Para fazer
            case 'all':
                rel = rel_builder.relatorio_completo(self, user) #Para fazer
            case _:
                pass        
        return rel
    def __init__(self) -> None:
        """Inicializa Acervo
        """
        self.estoque = {}  
        self.emprestimos_ativos = []

    def __iadd__(self, obra: Obra):
        """Função do operador +=, adiciona uma obra no estoque, caso já esteja nele, +1 quantidade
        
        Args:
            obra (Obra): obra que está sendo incrementada ao estoque
        """
        if obra.titulo in self.estoque:
            obra.quantidade += 1
        self.estoque[obra.titulo] = obra.quantidade

        return self

    def __isub__(self, obra: Obra):
        """Função do operador -=, -1 quantidade de uma obra, caso se torne 0, remove completamente do estoque
        
        Args:
            obra (Obra): Obra que está sendo decrementada do estoque
        """
        if obra.titulo in self.estoque:
            obra.quantidade -= 1
            self.estoque[obra.titulo] = obra.quantidade
        else:
            pass

        if obra.quantidade <= 0:
            self.estoque.pop(obra.titulo)

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

        Returns:
            Emprestimo: retorna o empréstimo que foi feito

        Raises:
            ValueError: Ocorre caso a obra não esteja em estoque    
        """
        if obra.disponivel(self.estoque):
            emp = Emprestimo(obra, usuario, date.today() + timedelta(days=dias))
            self.remover(obra)
            self.emprestimos_ativos.append(emp)
            usuario.emprestimos.append(emp)
            return emp
        else:
            raise ValueError

    def devolver(self, emprestimo: Emprestimo, data_dev: date = date.today()) -> None:
        """Finaliza um empréstimo, retornando a obra ao estoque
        
        Args:
            emprestimo (Emprestimo): Empréstimo realizado
            data_dev (date): Data em que a obra foi devolvida ( por padrão o dia atual )
        """
        self.multar_se_atrasado(emprestimo)

        self.adicionar(emprestimo.obra)
        emprestimo.marcar_devolucao(data_dev)
        self.emprestimos_ativos.remove(emprestimo)
    
    def renovar(self, emprestimo: Emprestimo, dias_extras: timedelta = timedelta(days=7)) -> None:
        """Adia a data de devolução de um empréstimo
        
        Args:
            emprestimo (Emprestimo): Empréstimo realizado
            dias_extras (timedelta): Dias adicionados
        """
        if emprestimo.dias_atraso() > dias_extras:
            return
            #Atraso tão grande que mesmo renovando ainda está atrasado, ainda estou vendo o que vou fazer

        self.multar_se_atrasado(emprestimo)
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

    def multar_se_atrasado(self, emprestimo: Emprestimo) -> None:
        """Verifica se o empréstimo está atrasado, e multa caso esteja
        
        Args:
            emprestimo (Emprestimo): emprestimo sendo verificado
        """
        if emprestimo.dias_atraso():
            emprestimo.usuario.debitos[f'Multa de atraso na devolução de {emprestimo.obra}, ocorreu em {date.today().strftime('%d/%m/%y')}.'] = f'R$ {self.valor_multa(emprestimo)}'.replace('.', ',')

    def _valida_obra(self, obra: Obra) -> bool:
        """Valida se uma obra é de fato da classe Obra

        Mesma função que isInstance(obra, Obra), não usado
        
        Args:
            obra (Obra): Obra que está sendo verificada
            
        Raises:
            TypeError: Caso a obra não seja da classe Obra
        """
        if not isinstance(obra, Obra):
            raise TypeError
