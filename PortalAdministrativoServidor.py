from concurrent import futures
import grpc
import json
import PortalAdministrativo_pb2_grpc
import PortalAdministrativo_pb2
import DatabaseService_pb2_grpc
import DatabaseService_pb2
import sys

class PortalAdministrativoServidor(PortalAdministrativo_pb2_grpc.PortalCadastroServicer):
    def __init__(self, portaDatabase):
        self.database_service_channel = grpc.insecure_channel(f'localhost:{portaDatabase}')
        self.database_service_stub = DatabaseService_pb2_grpc.DatabaseServiceStub(self.database_service_channel)

        self.database_service_stub.CreateTable(DatabaseService_pb2.TableMessage(tName="usuarios"))
        self.database_service_stub.CreateTable(DatabaseService_pb2.TableMessage(tName="usuariosLivros"))
        self.database_service_stub.CreateTable(DatabaseService_pb2.TableMessage(tName="livros"))

    def NovoUsuario(self, request, context):
        cpf, nome = request.cpf, request.nome

        try:
            if len(cpf) <= 3 or len(nome) <= 3:
                return PortalAdministrativo_pb2.Status(status=1, msg="CPF e Nome devem ter tamanho maior que 3 caracteres")

            response = self.database_service_stub.Create(DatabaseService_pb2.CreateUpdateMessage(tName="usuarios", key=cpf, value=json.dumps({"cpf":cpf , "nome":nome, "bloqueado": False})))
            
            if (response.status == 1):
                return PortalAdministrativo_pb2.Status(status=1, msg=response.msg)
            
            return PortalAdministrativo_pb2.Status(status=0, msg="Novo Usuário criado!")
        except grpc.RpcError:
            raise grpc.RpcError
    
    def EditaUsuario(self, request, context):
        cpf, nome = request.cpf, request.nome

        try:
            if len(cpf) <= 3 or len(nome) <= 3:
                return PortalAdministrativo_pb2.Status(status=1, msg="CPF e Nome devem ter tamanho maior que 3 caracteres")

            responseUsuario = self.database_service_stub.Request(DatabaseService_pb2.RequestMessage(tName="usuarios", key=cpf))
            if responseUsuario.value == "None":
                return PortalAdministrativo_pb2.Status(status=1, msg="Usuário não existe")
            
            usuario = json.loads(response.value)

            response = self.database_service_stub.Update(DatabaseService_pb2.CreateUpdateMessage(tName="usuarios", key=cpf, value=json.dumps({"cpf":cpf , "nome":nome, "bloqueado": usuario.get("bloqueado")})))
            
            if (response.status == 1):
                return PortalAdministrativo_pb2.Status(status=1, msg=response.msg)
            
            return PortalAdministrativo_pb2.Status(status=0, msg="Usuário editado!")
        except grpc.RpcError:
            raise grpc.RpcError
    
    def RemoveUsuario(self, request, context):
        cpf = request.id

        try:
            response = self.database_service_stub.Delete(DatabaseService_pb2.RequestMessage(tName="usuarios", key=cpf))
            
            if (response.status == 1):
                return PortalAdministrativo_pb2.Status(status=1, msg=response.msg)
            
            return PortalAdministrativo_pb2.Status(status=0, msg="Usuário removido com sucesso!")
        except grpc.RpcError:
            raise grpc.RpcError
        
    def ObtemUsuario(self, request, context):
        cpf = request.id

        try:
            response = self.database_service_stub.Request(DatabaseService_pb2.RequestMessage(tName="usuarios", key=cpf))
            if response.value != "None":
                usuario = json.loads(response.value)
                return PortalAdministrativo_pb2.Usuario(cpf=usuario.get('cpf'), nome=usuario.get('nome'))
            return PortalAdministrativo_pb2.Usuario()
        except grpc.RpcError:
            raise grpc.RpcError
        
    def ObtemTodosUsuarios(self, request, context):
        try:
            responses = self.database_service_stub.RequestAll(DatabaseService_pb2.TableMessage(tName="usuarios"))
            for response in responses:
                usuario = json.loads(response.value)
                yield PortalAdministrativo_pb2.Usuario(cpf=usuario.get('cpf'), nome=usuario.get('nome'))
        except grpc.RpcError:
            raise grpc.RpcError
        
    def NovoLivro(self, request, context):
        isbn, titulo, autor, total = request.isbn, request.titulo, request.autor, request.total

        try:
            if len(isbn) <= 3 or len(titulo) <= 3 or len(autor) <= 3:
                return PortalAdministrativo_pb2.Status(status=1, msg="ISBN, Título e Autor devem ter tamanho maior que 3 caracteres")

            response = self.database_service_stub.Create(DatabaseService_pb2.CreateUpdateMessage(tName="livros", key=isbn,
                value=json.dumps({"isbn": isbn, "titulo": titulo, "autor": autor, "total": total, "restante": total})))
            
            if (response.status == 1):
                return PortalAdministrativo_pb2.Status(status=1, msg=response.msg)
            
            return PortalAdministrativo_pb2.Status(status=0, msg="Novo Livro criado!")
        except grpc.RpcError:
            raise grpc.RpcError
    
    def EditaLivro(self, request, context):
        isbn, titulo, autor, total = request.isbn, request.titulo, request.autor, request.total

        try:
            if len(isbn) <= 3 or len(titulo) <= 3 or len(autor) <= 3:
                return PortalAdministrativo_pb2.Status(status=1, msg="ISBN, Título e Autor devem ter tamanho maior que 3 caracteres")

            responseLivro = self.database_service_stub.Request(DatabaseService_pb2.RequestMessage(tName="livros", key=isbn))
            if responseLivro.value == "None":
                return PortalAdministrativo_pb2.Status(status=1, msg="Livro não existe")
            
            livro = json.loads(response.value)

            if total < (livro.get("total") - livro.get("restante")):
                return PortalAdministrativo_pb2.Status(status=1, msg=f"O total é menor que o número de livros já emprestados. Quantidade de livros emprestados: {livro.get("total") - livro.get("restante")}")

            response = self.database_service_stub.Update(DatabaseService_pb2.CreateUpdateMessage(tName="livros", key=isbn,
                value=json.dumps({"isbn": isbn, "titulo": titulo, "autor": autor, "total": total, "restante": total})))
            
            if (response.status == 1):
                return PortalAdministrativo_pb2.Status(status=1, msg=response.msg)
            
            return PortalAdministrativo_pb2.Status(status=0, msg="Livro editado!")
        except grpc.RpcError:
            raise grpc.RpcError

    def RemoveLivro(self, request, context):
        isbn = request.id

        try:
            response = self.database_service_stub.Delete(DatabaseService_pb2.RequestMessage(tName="livros", key=isbn))
            
            if (response.status == 1):
                return PortalAdministrativo_pb2.Status(status=1, msg=response.msg)
            
            return PortalAdministrativo_pb2.Status(status=0, msg="Livro removido com sucesso!")
        except grpc.RpcError:
            raise grpc.RpcError
        
    def ObtemLivro(self, request, context):
        isbn = request.id

        try:
            response = self.database_service_stub.Request(DatabaseService_pb2.RequestMessage(tName="livros", key=isbn))
            if response.value != "None":
                livro = json.loads(response.value)
                return PortalAdministrativo_pb2.Livro(isbn=livro.get("isbn"), titulo=livro.get("titulo"), autor=livro.get("autor"), total=livro.get("total"))
            return PortalAdministrativo_pb2.Livro()
        except grpc.RpcError:
            raise grpc.RpcError
        
    def ObtemTodosLivros(self, request, context):
        try:
            responses = self.database_service_stub.RequestAll(DatabaseService_pb2.TableMessage(tName="livros"))
            for response in responses:
                livro = json.loads(response.value)
                yield PortalAdministrativo_pb2.Livro(isbn=livro.get("isbn"), titulo=livro.get("titulo"), autor=livro.get("autor"), total=livro.get("total"))
        except grpc.RpcError:
            raise grpc.RpcError

def run_server(porta: int, portaDatabase: int) -> None:
    class_work = PortalAdministrativoServidor(portaDatabase)

    server = None

    try:
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        PortalAdministrativo_pb2_grpc.add_PortalCadastroServicer_to_server(class_work, server)
        server.add_insecure_port(f'localhost:{porta}')
    except grpc.RpcError as e:
        print(f'Error during gRPC startup: {e}')

    server.start()

    print('Server listening on port ' + str(porta) + '...')

    server.wait_for_termination()


if __name__ == '__main__':
    try:
        porta = int(sys.argv[1])
        portaDatabase = int(sys.argv[2])
    except Exception:
        porta = 99922

    run_server(porta, portaDatabase)