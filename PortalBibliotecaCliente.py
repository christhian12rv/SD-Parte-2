import grpc
import PortalBiblioteca_pb2_grpc
import PortalBiblioteca_pb2
import sys

def geraEmprestimo(cpf: str, isbn: str):
    yield PortalBiblioteca_pb2.UsuarioLivro(
        usuario=PortalBiblioteca_pb2.Identificador(id=cpf),
        livro=PortalBiblioteca_pb2.Identificador(id=isbn)
    )

def realizaDevolucao(cpf: str, isbn: str):
    yield PortalBiblioteca_pb2.UsuarioLivro(
        usuario=PortalBiblioteca_pb2.Identificador(id=cpf),
        livro=PortalBiblioteca_pb2.Identificador(id=isbn)
    )

class PortalBibliotecaCliente:
    def __init__(self, porta: int):
        self.porta = porta
      
    def realizaEmprestimo(self, cpf: str, isbn: str) -> None:
        with grpc.insecure_channel(f'localhost:{self.porta}') as channel:
            stub = PortalBiblioteca_pb2_grpc.PortalBibliotecaStub(channel)
                                    
            try:
                response = stub.RealizaEmprestimo(geraEmprestimo(cpf, isbn))
                print()
                if response.status == 0:
                    print('Empréstimo realizado com sucesso')
                else:
                    print(f'{response.msg}')
            except grpc.RpcError as e:
                print(f'Erro ao realizar empréstimo: {e}')
    
    def realizaDevolucao(self, cpf: str, isbn: str) -> None:
        with grpc.insecure_channel(f'localhost:{self.porta}') as channel:
            stub = PortalBiblioteca_pb2_grpc.PortalBibliotecaStub(channel)
                                    
            try:
                response = stub.RealizaDevolucao(realizaDevolucao(cpf, isbn))
                print()
                if response.status == 0:
                    print('Devolução realizada com sucesso')
                else:
                    print(f'{response.msg}')
            except grpc.RpcError as e:
                print(f'Erro ao realizar devolução: {e}')
        
    def bloqueiaUsuarios(self) -> None:
        with grpc.insecure_channel(f'localhost:{self.porta}') as channel:
            stub = PortalBiblioteca_pb2_grpc.PortalBibliotecaStub(channel)
                                    
            try:
                response = stub.BloqueiaUsuarios(PortalBiblioteca_pb2.Vazia())
                print()
                if response.status == 1:
                    print('Usuários bloqueados com sucesso, quantidade: ', response.msg)
                else:
                    print(f'{response.msg}')
            except grpc.RpcError as e:
                print(f'Erro ao bloquear usuários: {e}')
        
    def liberaUsuarios(self) -> None:
        with grpc.insecure_channel(f'localhost:{self.porta}') as channel:
            stub = PortalBiblioteca_pb2_grpc.PortalBibliotecaStub(channel)
                                    
            try:
                response = stub.LiberaUsuarios(PortalBiblioteca_pb2.Vazia())
                print()
                if response.status == 1:
                    print('Usuários liberados com sucesso, quantidade: ', response.msg)
                else:
                    print(f'{response.msg}')
            except grpc.RpcError as e:
                print(f'Erro ao liberados usuários: {e}')

    def listaUsuariosBloqueados(self) -> None:
        with grpc.insecure_channel(f'localhost:{self.porta}') as channel:
            stub = PortalBiblioteca_pb2_grpc.PortalBibliotecaStub(channel)
                                    
            try:
                response = stub.ListaUsuariosBloqueados(PortalBiblioteca_pb2.Vazia())
                print()

                for usuariosLivros in response:
                    print("\nUsuário cpf: ", usuariosLivros.usuario.cpf)
                    print("Nome: ", usuariosLivros.usuario.nome)
                    print("Livros")
                    for livro in usuariosLivros.livros:
                        print('\nISBN: ', livro.isbn)
                        print('Título: ', livro.titulo)
                        print('Autor: ', livro.autor)
                        print('Total: ', livro.total)
                        print('Restante: ', livro.restante)
            except grpc.RpcError as e:
                print(f'Erro ao listar livros emprestados: {e}')
    
    def listaLivrosEmprestados(self) -> None:
        with grpc.insecure_channel(f'localhost:{self.porta}') as channel:
            stub = PortalBiblioteca_pb2_grpc.PortalBibliotecaStub(channel)
                                    
            try:
                response = stub.ListaLivrosEmprestados(PortalBiblioteca_pb2.Vazia())
                print()

                for livro in response:
                    print('\nISBN: ', livro.isbn)
                    print('Título: ', livro.titulo)
                    print('Autor: ', livro.autor)
                    print('Total: ', livro.total)
                    print('Restante: ', livro.restante)
            except grpc.RpcError as e:
                print(f'Erro ao listar livros emprestados: {e}')
            
    def listaLivrosEmFalta(self) -> None:
        with grpc.insecure_channel(f'localhost:{self.porta}') as channel:
            stub = PortalBiblioteca_pb2_grpc.PortalBibliotecaStub(channel)
                                    
            try:
                response = stub.ListaLivrosEmFalta(PortalBiblioteca_pb2.Vazia())
                print()

                for livro in response:
                    print('\nISBN: ', livro.isbn)
                    print('Título: ', livro.titulo)
                    print('Autor: ', livro.autor)
                    print('Total: ', livro.total)
                    print('Restante: ', livro.restante)
            except grpc.RpcError as e:
                print(f'Erro ao listar livros emprestados: {e}')

    def pesquisaLivro(self, criterioPesquisa: str) -> None:
        with grpc.insecure_channel(f'localhost:{self.porta}') as channel:
            stub = PortalBiblioteca_pb2_grpc.PortalBibliotecaStub(channel)
                                    
            try:
                response = stub.PesquisaLivro(
                    PortalBiblioteca_pb2.Criterio(criterio=criterioPesquisa)
                )
                print()
                for livro in response:
                    print('\nISBN: ', livro.isbn)
                    print('Título: ', livro.titulo)
                    print('Autor: ', livro.autor)
                    print('Total: ', livro.total)
                    print('Restante: ', livro.restante)
            except grpc.RpcError as e:
                print(f'Erro ao listar livros emprestados: {e}')

def menu_opcoes() -> None:
    print()
    print('#' * 20)
    print('1 - Realiza Empréstimo')
    print('2 - Realiza Devolução')
    print('3 - Bloqueia Usuários')
    print('4 - Libera Usuários')
    print('5 - Lista Usuários Bloqueados')
    print('6 - Lista Livros Emprestados')
    print('7 - Lista Livros em Falta')
    print('8 - Pesquisa Livro')
    print('#' * 20)


def menu(PortalAdmin: PortalBibliotecaCliente) -> None:
    while True:
        menu_opcoes()
        opcoes = int(input('Digite uma opção: '))

        match opcoes:
            case 1:
                cpf = input('Digite o cpf: ')
                isbn = input('Digite o isbn: ')

                PortalAdmin.realizaEmprestimo(cpf, isbn)
            case 2:
                cpf = input('Digite o cpf: ')
                isbn = input('Digite o isbn: ')

                PortalAdmin.realizaDevolucao(cpf, isbn)
            case 3:
                PortalAdmin.bloqueiaUsuarios()
            case 4:
                PortalAdmin.liberaUsuarios()
            case 5:
                PortalAdmin.listaUsuariosBloqueados()
            case 6:
                PortalAdmin.listaLivrosEmprestados()
            case 7:
                PortalAdmin.listaLivrosEmFalta()
            case 8:
                criterioPesquisa = input('Critério de pesquisa: ')
                PortalAdmin.pesquisaLivro(criterioPesquisa)
            case _:
                print('Digite uma entrada válida')

if __name__ == '__main__':
    try:
        porta = int(sys.argv[1])
    except Exception:
        porta = 99921

    Portal = PortalBibliotecaCliente(porta)

    menu(Portal)
