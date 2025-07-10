from datetime import date
from datetime import timedelta
import uuid

class BaseEntity:
    """Classe pai, usada para a criação de um id único e comparação ==.

    Attributes:
        id (UUID): id gerado pelo uuid4(), único
        data_criacao (date): data em que a instância foi criada
    """

    __slots__ = ['id', 'data_criacao']

    def __init__(self) -> None:
        """Inicializa BaseEntity.
        """
        self.id = self._gerar_id
        self.data_criacao = date.today()

    def __eq__(self, other) -> bool:
        """Compara instâncias de BaseEntity, verificando se são do mesmo tipo e possuem o mesmo id.
        
        Args:
            other (BaseEntity): a outra instância da comparação

        Returns:
            bool: True caso iguais ( mesmo id e classe ), False caso contrário
        """
        if isinstance(other, type(self)) and other.id == self.id:
            return True
        else:
            return False
        
    def _gerar_id(self) -> uuid.UUID:
        """Gera um id com a biblioteca uuid4(), para usar no __init__.
        
        Returns:
            UUID: um id único gerado pelo uuid4()
        """
        return uuid.uuid4()

class Obra(BaseEntity):
    """Uma obra única usada no acervo.
    
    Attributes:
        id (UUID): id gerado pelo uuid4(), único
        data_criacao (date): data em que a instância foi criada
        titulo (str): título da obra
        autor (str): autor da obra
        ano (int): ano em que a obra foi publicada
        categoria (str): categoria da obra
        quantidade (int): quantidade da obra
    """

    __slots__ = ['titulo', 'autor', 'ano', 'categoria', 'quantidade']

    def __init__(self, titulo: str, autor: str, ano: int, categoria: str, quantidade: int = 1) -> None:
        """Inicializa Obra.

        Args:
            titulo (str): título da obra
            autor (str): autor da obra
            ano (int): ano em que a obra foi publicada
            categoria (str): categoria da obra
            quantidade (int): quantidade da obra, padrão 1 ( é o esperado na criação da obra )
        """
        super().__init__()
        self.titulo = titulo
        self.autor = autor
        self.ano = ano
        self.categoria = categoria
        self.quantidade = quantidade

    def disponivel(self, estoque: dict) -> bool:
        """Verifica se a obra está no estoque do acervo.

        Args:
            estoque (dict): acervo.estoque, dicionário com todas as obras e suas quantidades

        Returns:
            bool: True caso esteja no estoque, False caso contrário
        """
        if self.titulo in estoque:
            return True
        else: 
            return False
        
    def __str__(self) -> str:
        """Retorna uma string para representar o objeto.
        
        Returns:
            str: Nome e ano da obra
        """
        return f'"{self.titulo}", {self.autor}'
        
class Usuario(BaseEntity):
    """Um usuário do serviço de acervo.

    Attributes:
        id (UUID): id gerado pelo uuid4(), único
        data_criacao (date): data em que a instância foi criada
        nome (str): nome do usuário
        email (str): email do usuário
        emprestimos (list): lista de empréstimos já feitos
        debitos (dict): lista de débitos já feitos, no formato {"motivo": preço}
        historico (list, de classe): Armazena todos os usuários
    """

    __slots__ = ['nome', 'email', 'emprestimos', 'debitos']

    historico = []

    def __init__(self, nome: str, email: str) -> None:
        """Inicializa Usuario.
        
        Args:
            nome (str): nome do usuário
            email (str): email do usuário
        """

        super().__init__()
        self.nome = nome
        self.email = email
        self.emprestimos = []
        self.debitos = {}
        Usuario.historico.append(self)

    def __lt__(self, other) -> bool:
        """Compara instâncias do Usuario, usando seus nomes como parâmetro de verificação.
        
        Args:
            other (Usuario): a outra instância da comparação

        Returns:
            bool: True caso menor que, False caso contrário
        """
        return self.nome < other.nome
    
    def __gt__(self, other) -> bool:
        """Compara instâncias do Usuario, usando seus nomes como parâmetro de verificação.
        
        Args:
            other (Usuario): a outra instância da comparação

        Returns:
            bool: True caso maior que, False caso contrário
        """
        return self.nome > other.nome
    
    def __str__(self) -> str:
        """Retorna uma string para representar o objeto.
        
        Returns:
            str: nome do usuário
        """
        return self.nome
    
class Emprestimo(BaseEntity):
    """Representa um empréstimo, associando o usuário com a obra emprestada.
    
    Attributes:
        id (UUID): id gerado pelo uuid4(), único
        data_criacao (date): data em que a instância foi criada
        obra (Obra): Obra associada ao empréstimo
        usuario (Usuario): Usuário associada ao empréstimo
        data_prev_devol (date): Data prevista para devolução
        data_retirada (date): Data em que ocorreu o empréstimo
        data_dev_real (date):  Data em que ocorrerá a devolução, maior prioridade, mas por padrão, None
        historico (list, de classe): Armazena todos os empréstimos já registrados
    """

    __slots__ = ['obra', 'usuario', 'data_prev_devol', 'data_retirada', 'data_dev_real']

    historico = []

    def __init__(self, obra: Obra, usuario: Usuario, data_prev_devol: date = date.today() + timedelta(days=7), data_retirada: date = date.today()) -> None:
        """Inicializa Emprestimo.

        Args:
            obra (Obra): Obra associada ao empréstimo
            usuario (Usuario): Usuário associada ao empréstimo
            data_prev_devol (date): Data prevista para devolução ( por padrão, 7 dias no futuro )
            data_retirada (date): Data em que ocorreu o empréstimo ( por padrão o dia atual, date.today() )
        """

        super().__init__()
        self.obra = obra
        self.usuario = usuario
        self.data_retirada = data_retirada
        self.data_prev_devol = data_prev_devol
        self.data_dev_real = None
        Emprestimo.historico.append(self)

    def marcar_devolucao(self, data_dev_real: date) -> None:
        """Registra data de devolução.

        Args:
            data_dev_real (date): Data de devolução real
        """
        self.data_dev_real = data_dev_real

    def dias_atraso(self, data_ref: date = date.today()) -> int:
        """Calcula quantos dias de atraso entre a data de referência e a data de devolução, retorna 0 caso em dia

        Args:
            data_ref (date): Data de referência para a comparação, ( por padrão o dia atual )

        Returns:
            int: Quantidade de dias que a devolução está em atraso, retorna 0 caso esteja em dia
        """
        return abs((self.data_prev_devol - data_ref).days)

    def __str__(self) -> str:
        """Retorna uma string para representar o objeto no print.
        
        Returns:
            str: 'prev: dd/mm'
        """
        string = f'Empréstimo da obra {self.obra}'
        if not self.data_dev_real:
            string += f', Data prev de devolução: {self.data_prev_devol}'
            if self.dias_atraso():
                string += f', Atrasado.'
            else:
                string += f', Em dia.'
        else:
            string += f', Devolvido em {self.data_dev_real.strftime('%d/%m/%y')}.'
