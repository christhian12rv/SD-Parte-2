import grpc
import PortalAdministrativo_pb2_grpc
import PortalAdministrativo_pb2
import sys

class PortalAdministrativoCliente:
    def __init__(self, porta: int):
        self.porta = porta
      
    def novoUsuario(self, cpf: str, nome: str) -> None:
        with grpc.insecure_channel(f'localhost:{self.porta}') as channel:
            stub = PortalAdministrativo_pb2_grpc.PortalCadastroStub(channel)
                                    
            try:
                response = stub.NovoUsuario(
                  	PortalAdministrativo_pb2.Usuario(
                        cpf=cpf,
                        nome=nome
					)
				)
                print()
                if response.status == 0:
                    print('Usuário criado com sucesso')
                else:
                    print(f'{response.msg}')
            except grpc.RpcError as e:
                print(f'Erro ao cadastrar Usuário: {e}')

    def editaUsuario(self, cpf: str, nome: str) -> None:
        with grpc.insecure_channel(f'localhost:{self.porta}') as channel:
            stub = PortalAdministrativo_pb2_grpc.PortalCadastroStub(channel)
                                    
            try:
                response = stub.EditaUsuario(
                  	PortalAdministrativo_pb2.Usuario(
                        cpf=cpf,
                        nome=nome
					)
				)
                print()
                if response.status == 0:
                    print('Usuário editado com sucesso')
                else:
                    print(f'{response.msg}')
            except grpc.RpcError as e:
                print(f'Erro ao editar Usuário: {e}')

    def removeUsuario(self, cpf: str) -> None:
        with grpc.insecure_channel(f'localhost:{self.porta}') as channel:
            stub = PortalAdministrativo_pb2_grpc.PortalCadastroStub(channel)
                                    
            try:
                response = stub.RemoveUsuario(
                  	PortalAdministrativo_pb2.Identificador(
                        id=cpf
					)
				)
                print()
                if response.status == 0:
                    print('Usuário removido com sucesso')
                else:
                     print(f'{response.msg}')
            except grpc.RpcError as e:
                print(f'Erro ao remover Usuário: {e}')
    
    def obtemUsuario(self, cpf: str) -> None:
        with grpc.insecure_channel(f'localhost:{self.porta}') as channel:
            stub = PortalAdministrativo_pb2_grpc.PortalCadastroStub(channel)
                                    
            try:
                response = stub.ObtemUsuario(
                  	PortalAdministrativo_pb2.Identificador(
                        id=cpf
					)
				)
                print()
                if response.cpf:
                    print('Usuário encontrado\n', response)
                else:
                    print('Usuário não encontrado')
            except grpc.RpcError as e:
                print(f'Erro ao buscar Usuário: {e}')
    
    def obtemTodosUsuarios(self) -> None:
        with grpc.insecure_channel(f'localhost:{self.porta}') as channel:
            stub = PortalAdministrativo_pb2_grpc.PortalCadastroStub(channel)
                                    
            try:
                response = stub.ObtemTodosUsuarios(PortalAdministrativo_pb2.Vazia())
                print()

                for usuario in response:
                    print('\nCPF: ', usuario.cpf)
                    print('Nome: ', usuario.nome)
            except grpc.RpcError as e:
                print(f'Erro ao buscar Usuários: {e}')
            
    def novoLivro(self, isbn: str, titulo: str, autor: str, total: int) -> None:
        with grpc.insecure_channel(f'localhost:{self.porta}') as channel:
            stub = PortalAdministrativo_pb2_grpc.PortalCadastroStub(channel)
                                    
            try:
                response = stub.NovoLivro(
                  	PortalAdministrativo_pb2.Livro(
                        isbn=isbn,
                        titulo=titulo,
                        autor=autor,
                        total=total
					)
				)
                print()
                if response.status == 0:
                    print('Livro criado com sucesso')
                else:
                    print(f'{response.msg}')
            except grpc.RpcError as e:
                print(f'Erro ao cadastrar Livro: {e}')

    def editaLivro(self, isbn: str, titulo: str, autor: str, total: int) -> None:
        with grpc.insecure_channel(f'localhost:{self.porta}') as channel:
            stub = PortalAdministrativo_pb2_grpc.PortalCadastroStub(channel)
                                    
            try:
                response = stub.EditaLivro(
                  	PortalAdministrativo_pb2.Livro(
                        isbn=isbn,
                        titulo=titulo,
                        autor=autor,
                        total=total
					)
				)
                print()
                if response.status == 0:
                    print('Livro editado com sucesso')
                else:
                    print(f'{response.msg}')
            except grpc.RpcError as e:
                print(f'Erro ao editar Livro: {e}')

    def removeLivro(self, isbn: str) -> None:
        with grpc.insecure_channel(f'localhost:{self.porta}') as channel:
            stub = PortalAdministrativo_pb2_grpc.PortalCadastroStub(channel)
                                    
            try:
                response = stub.RemoveLivro(
                  	PortalAdministrativo_pb2.Identificador(
                        id=isbn
					)
				)
                print()
                if response.status == 0:
                    print('Livro removido com sucesso')
                else:
                     print(f'{response.msg}')
            except grpc.RpcError as e:
                print(f'Erro ao remover Livro: {e}')

    def obtemLivro(self, isbn: str) -> None:
        with grpc.insecure_channel(f'localhost:{self.porta}') as channel:
            stub = PortalAdministrativo_pb2_grpc.PortalCadastroStub(channel)
                                    
            try:
                response = stub.ObtemLivro(
                  	PortalAdministrativo_pb2.Identificador(
                        id=isbn
					)
				)
                print(response)
                print()
                if response.isbn:
                    print('Livro encontrado\n', response)
                else:
                    print('Livro não encontrado')
            except grpc.RpcError as e:
                print(f'Erro ao buscar Livro: {e}')

    def obtemTodosLivros(self) -> None:
        with grpc.insecure_channel(f'localhost:{self.porta}') as channel:
            stub = PortalAdministrativo_pb2_grpc.PortalCadastroStub(channel)
                                    
            try:
                response = stub.ObtemTodosLivros(PortalAdministrativo_pb2.Vazia())

                for livro in response:
                    print('\nISBN: ', livro.isbn)
                    print('Título: ', livro.titulo)
                    print('Autor: ', livro.autor)
                    print('Total: ', livro.total)
            except grpc.RpcError as e:
                print(f'Erro ao buscar Livros: {e}')

def menu_opcoes() -> None:
    print()
    print('#' * 20)
    print('1 - Novo Usuário')
    print('2 - Edita Usuário')
    print('3 - Remove Usuário')
    print('4 - Obtém Usuário')
    print('5 - Obtém Todos Usuários')
    print('6 - Novo Livro')
    print('7 - Edita Livro')
    print('8 - Remove Livro')
    print('9 - Obtém Livro')
    print('10 - Obtém Todos Livros')
    print('#' * 20)


def menu(PortalAdmin: PortalAdministrativoCliente) -> None:
    while True:
        menu_opcoes()
        opcoes = int(input('Digite uma opção: '))

        match opcoes:
            case 1:
                cpf = input('Digite o cpf: ')
                nome = input('Digite o nome: ')

                PortalAdmin.novoUsuario(cpf, nome)
            case 2:
                cpf = input('Digite o cpf: ')
                nome = input('Digite o novo nome: ')

                PortalAdmin.editaUsuario(cpf, nome)
            case 3:
                cpf = input('Digite o cpf: ')

                PortalAdmin.removeUsuario(cpf)
            case 4:
                cpf = input('Digite o cpf: ')

                PortalAdmin.obtemUsuario(cpf)
            case 5:
                PortalAdmin.obtemTodosUsuarios()
            case 6:
                isbn = input('Digite o isbn: ')
                titulo = input('Digite o título: ')
                autor = input('Digite o autor: ')
                total = input('Digite o total: ')

                PortalAdmin.novoLivro(isbn, titulo, autor, int(total))
            case 7:
                isbn = input('Digite o isbn: ')
                titulo = input('Digite o título: ')
                autor = input('Digite o autor: ')
                total = input('Digite o total: ')

                PortalAdmin.editaLivro(isbn, titulo, autor, int(total))
            case 8:
                isbn = input('Digite o isbn: ')

                PortalAdmin.removeLivro(isbn)
            case 9:
                isbn = input('Digite o isbn: ')

                PortalAdmin.obtemLivro(isbn)
            case 10:
                PortalAdmin.obtemTodosLivros()
            case _:
                print('Digite uma entrada válida')

if __name__ == '__main__':
    try:
        porta = int(sys.argv[1])
    except Exception:
        porta = 99922

    Portal = PortalAdministrativoCliente(porta)

    menu(Portal)
