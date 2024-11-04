from concurrent import futures
from datetime import datetime
import grpc
import PortalBiblioteca_pb2_grpc
import PortalBiblioteca_pb2
import DatabaseService_pb2_grpc
import DatabaseService_pb2
import re
import sys
import json

SECONDS_TO_BLOCK = 10

def dateDiffInSeconds(dt2, dt1):
    timedelta = dt2 - dt1
    return timedelta.days * 24 * 3600 + timedelta.seconds


class PortalBibliotecaServidor(PortalBiblioteca_pb2_grpc.PortalBibliotecaServicer):
    def __init__(self, portaDatabase):
        # json_data = '{}'
        # self.usuarios = json.loads(json_data)
        # self.livros = json.loads(json_data)
        # self.usuariosLivros = json.loads(json_data)

        self.database_service_channel = grpc.insecure_channel(f'localhost:{portaDatabase}')
        self.database_service_stub = DatabaseService_pb2_grpc.DatabaseServiceStub(self.database_service_channel)

        self.database_service_stub.CreateTable(DatabaseService_pb2.TableMessage(tName="usuarios"))
        self.database_service_stub.CreateTable(DatabaseService_pb2.TableMessage(tName="usuariosLivros"))
        self.database_service_stub.CreateTable(DatabaseService_pb2.TableMessage(tName="livros"))
        
    def RealizaEmprestimo(self, request_iterator, context):
        for request in request_iterator:
            cpf, isbn = request.usuario.id, request.livro.id

            try:
                responseUsuario = self.database_service_stub.Request(DatabaseService_pb2.RequestMessage(tName="usuarios", key=cpf))
                if responseUsuario.value == "None":
                    return PortalBiblioteca_pb2.Status(status=1, msg="Usuário não existe")
                
                responseLivro = self.database_service_stub.Request(DatabaseService_pb2.RequestMessage(tName="livros", key=isbn))
                if responseLivro.value == "None":
                    return PortalBiblioteca_pb2.Status(status=1, msg="Livro não existe")
                
                usuario = json.loads(responseUsuario.value)
                livro = json.loads(responseLivro.value)
                
                if usuario.get("bloqueado"):
                    return PortalBiblioteca_pb2.Status(status=1, msg="Usuário está bloqueado")

                if livro.get("restante") < 1:
                    return PortalBiblioteca_pb2.Status(status=1, msg="Livro não está disponível")
                
                responseUsuariosLivrosRelation = self.database_service_stub.Request(DatabaseService_pb2.RequestMessage(tName="usuariosLivros", key=cpf))
                
                if responseUsuariosLivrosRelation.value != "None":
                    usuariosLivrosRelation = json.loads(responseUsuariosLivrosRelation.value)
                else:
                    usuariosLivrosRelation = {'cpf': usuario.get("cpf")}

                if usuariosLivrosRelation.get("livros") is None:
                    usuariosLivrosRelation.update({'livros': [] })

                usuariosLivrosRelation.get("livros").append({'isbn': livro.get("isbn"), 'dataEmprestimo': datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                
                response = self.database_service_stub.Update(DatabaseService_pb2.CreateUpdateMessage(tName="livros", key=isbn,
                    value=json.dumps({"isbn": isbn, "titulo": livro.get("titulo"), "autor": livro.get("autor"), "total": livro.get("total"), "restante": (livro.get("restante") - 1)})))

                response = self.database_service_stub.Create(DatabaseService_pb2.CreateUpdateMessage(tName="usuariosLivros", key=cpf, value=json.dumps(usuariosLivrosRelation)))
                
                if (response.status == 1):
                    return PortalBiblioteca_pb2.Status(status=1, msg=response.msg)
            
                return PortalBiblioteca_pb2.Status(status=0, msg="Empréstimo realizado com sucesso!")
            except grpc.RpcError:
                raise grpc.RpcError

        return PortalBiblioteca_pb2.Status(status=0, msg="Empréstimo realizado com sucesso!")
            
    def RealizaDevolucao(self, request_iterator, context):
        for request in request_iterator:
            cpf, isbn = request.usuario.id, request.livro.id

            try:
                responseUsuario = self.database_service_stub.Request(DatabaseService_pb2.RequestMessage(tName="usuarios", key=cpf))
                if responseUsuario.value == "None":
                    return PortalBiblioteca_pb2.Status(status=1, msg="Usuário não existe")
                
                responseLivro = self.database_service_stub.Request(DatabaseService_pb2.RequestMessage(tName="livros", key=isbn))
                if responseLivro.value == "None":
                    return PortalBiblioteca_pb2.Status(status=1, msg="Livro não existe")
                
                usuario = json.loads(responseUsuario.value)
                livro = json.loads(responseLivro.value)

                responseUsuariosLivrosRelation = self.database_service_stub.Request(DatabaseService_pb2.RequestMessage(tName="usuariosLivros", key=cpf))
                
                if responseUsuariosLivrosRelation.value == "None":
                    return PortalBiblioteca_pb2.Status(status=1, msg="Esse usuário não possui nenhum livro emprestado!")
                
                usuariosLivrosRelation = json.loads(responseUsuariosLivrosRelation.value)
                livrosEmprestados = usuariosLivrosRelation.get("livros")

                if not any(livro.get("isbn") == isbn for livro in livrosEmprestados):
                    return PortalBiblioteca_pb2.Status(status=1, msg="Esse livro não está emprestado para esse usuário")

                # Remove o livro de self.usuariosLivros[cpf]
                for livroEmprestado in livrosEmprestados:
                    if livroEmprestado.get('isbn') == isbn:
                        livrosEmprestados.remove(livroEmprestado)
                        break

                if len(livrosEmprestados) < 1:
                    self.database_service_stub.Delete(DatabaseService_pb2.RequestMessage(tName="livrosEmprestados", key=usuario.get("cpf")))
                else:
                    usuariosLivrosRelation.update({"livros": livrosEmprestados})
                    self.database_service_stub.Update(DatabaseService_pb2.CreateUpdateMessage(tName="usuariosLivros", key=cpf, value=json.dumps(usuariosLivrosRelation)))

                livro.update({"restante": (livro.get("restante") + 1)})

                if usuario.get("bloqueado"):
                    if len(livrosEmprestados) < 1:
                        usuario.update({"bloqueado": False})
                    else:
                        todosDentroPrazo = True
                        now = datetime.now()
                        for livro in livrosEmprestados:
                            dataEmprestimo = datetime.strptime(livro.get('dataEmprestimo'), "%Y-%m-%d %H:%M:%S")
                            if dateDiffInSeconds(now, dataEmprestimo) > SECONDS_TO_BLOCK:
                                todosDentroPrazo = False
                                break
                        if todosDentroPrazo:
                            usuario.update({"bloqueado": False})
                        
                    self.database_service_stub.Update(DatabaseService_pb2.CreateUpdateMessage(tName="usuarios", key=cpf, value=json.dumps(usuario)))
            
                self.database_service_stub.Update(DatabaseService_pb2.CreateUpdateMessage(tName="livros", key=isbn, value=json.dumps(livro)))
            except grpc.RpcError:
                raise grpc.RpcError
        
        return PortalBiblioteca_pb2.Status(status=0, msg="Devolução realizada com sucesso!")
    
    def BloqueiaUsuarios(self, request, context):
        try:
            usuariosBloqueados = 0

            responseUsuariosLivrosRelation = self.database_service_stub.RequestAll(DatabaseService_pb2.TableMessage(tName="usuariosLivros"))
            
            for usuarioLivro in responseUsuariosLivrosRelation:
                usuarioLivro = json.loads(usuarioLivro.value)
                responseUsuario = self.database_service_stub.Request(DatabaseService_pb2.RequestMessage(tName="usuarios", key=usuarioLivro.get("cpf")))
                if responseUsuario.value == "None":
                    continue
                
                usuario = json.loads(responseUsuario.value)
                if usuario.get("bloqueado"):
                    continue

                now = datetime.now()

                for livro in usuarioLivro.get("livros"):
                    dataEmprestimo = datetime.strptime(livro.get('dataEmprestimo'), "%Y-%m-%d %H:%M:%S")
                    if dateDiffInSeconds(now, dataEmprestimo) > SECONDS_TO_BLOCK:
                        usuario.update({"bloqueado": True})
                        print(usuario)
                        self.database_service_stub.Update(DatabaseService_pb2.CreateUpdateMessage(tName="usuarios", key=usuario.get("cpf"), value=json.dumps(usuario)))
                        usuariosBloqueados += 1
                        break

            if usuariosBloqueados < 1:
                return PortalBiblioteca_pb2.Status(status=0, msg="Nenhum usuário foi bloqueado")

            message = f'{usuariosBloqueados}'
            return PortalBiblioteca_pb2.Status(status=1, msg=message)
        except grpc.RpcError:
            raise grpc.RpcError
        
    def LiberaUsuarios(self, request, context):
        try:
            usuariosLiberados = 0

            responseUsuarios = self.database_service_stub.RequestAll(DatabaseService_pb2.TableMessage(tName="usuarios"))
            
            for responseUsuario in responseUsuarios:
                usuario = json.loads(responseUsuario.value)

                if not usuario.get("bloqueado"):
                    continue

                now = datetime.now()

                responseUsuariosLivrosRelation = self.database_service_stub.Request(DatabaseService_pb2.RequestMessage(tName="usuariosLivros", key=usuario.get("cpf")))
                
                if responseUsuariosLivrosRelation.value == "None":
                    usuario.update({"bloqueado": False})
                    self.database_service_stub.Update(DatabaseService_pb2.CreateUpdateMessage(tName="usuarios", key=usuario.get("cpf"), value=json.dumps(usuario)))
                    usuariosLiberados += 1
                    continue
                
                usuariosLivrosRelation = json.loads(responseUsuariosLivrosRelation.value)
                livrosEmprestados = usuariosLivrosRelation.get("livros")

                for livro in livrosEmprestados:
                    dataEmprestimo = datetime.strptime(livro.get('dataEmprestimo'), "%Y-%m-%d %H:%M:%S")
                    if dateDiffInSeconds(now, dataEmprestimo) <= SECONDS_TO_BLOCK:
                        usuario.update({"bloqueado": False})
                        self.database_service_stub.Update(DatabaseService_pb2.CreateUpdateMessage(tName="usuarios", key=usuario.get("cpf"), value=json.dumps(usuario)))
                        usuariosLiberados += 1
                        break

            if usuariosLiberados < 1:
                return PortalBiblioteca_pb2.Status(status=0, msg="Nenhum usuário foi liberado")

            message = f'{usuariosLiberados}'
            return PortalBiblioteca_pb2.Status(status=1, msg=message)
        except grpc.RpcError:
            raise grpc.RpcError
        
    def ListaUsuariosBloqueados(self, request, context):
        try:
            responseUsuarios = self.database_service_stub.RequestAll(DatabaseService_pb2.TableMessage(tName="usuarios"))
            
            for responseUsuario in responseUsuarios:
                usuario = json.loads(responseUsuario.value)

                if usuario.get("bloqueado"):
                    responseUsuariosLivrosRelation = self.database_service_stub.Request(DatabaseService_pb2.RequestMessage(tName="usuariosLivros", key=usuario.get("cpf")))
                
                    if responseUsuariosLivrosRelation.value == "None":
                        yield PortalBiblioteca_pb2.UsuarioBloqueado(usuario=usuario, livros=[])
                        continue
                    
                    usuariosLivrosRelation = json.loads(responseUsuariosLivrosRelation.value)

                    livrosQueCausaramBloqueio = []
                    now = datetime.now()

                    for livroRelation in usuariosLivrosRelation.get("livros"):
                        dataEmprestimo = datetime.strptime(livroRelation.get('dataEmprestimo'), "%Y-%m-%d %H:%M:%S")
                        if dateDiffInSeconds(now, dataEmprestimo) > SECONDS_TO_BLOCK:
                            responseLivro = self.database_service_stub.Request(DatabaseService_pb2.RequestMessage(tName="livros", key=livroRelation.get("isbn")))
                        
                            if responseLivro.value == "None":
                                continue
                            
                            livro = json.loads(responseLivro.value)
                            livrosQueCausaramBloqueio.append(livro)

                    yield PortalBiblioteca_pb2.UsuarioBloqueado(usuario=usuario, livros=livrosQueCausaramBloqueio)
        except grpc.RpcError:
            raise grpc.RpcError
        
    def ListaLivrosEmprestados(self, request, context):
        try:
            responseLivros = self.database_service_stub.RequestAll(DatabaseService_pb2.TableMessage(tName="livros"))
            
            for responseLivro in responseLivros:
                livro = json.loads(responseLivro.value)

                if livro.get("total") != livro.get("restante"):
                    yield PortalBiblioteca_pb2.Livro(isbn=livro.get("isbn"), titulo=livro.get("titulo"),
                        autor=livro.get("autor"), total=livro.get("total"), restante=livro.get("restante"))
        except grpc.RpcError:
            raise grpc.RpcError
        
    def ListaLivrosEmFalta(self, request, context):
        try:
            responseLivros = self.database_service_stub.RequestAll(DatabaseService_pb2.TableMessage(tName="livros"))
            
            for responseLivro in responseLivros:
                livro = json.loads(responseLivro.value)

                if livro.get("restante") == 0:
                    yield PortalBiblioteca_pb2.Livro(isbn=livro.get("isbn"), titulo=livro.get("titulo"),
                        autor=livro.get("autor"), total=livro.get("total"), restante=livro.get("restante"))
        except grpc.RpcError:
            raise grpc.RpcError

    def PesquisaLivro(self, request, context):
        criterioPesquisa = request.criterio
        
        try:
            criterio_regex = r"(isbn|titulo|autor):([^\s&|]+)"
            criterios = re.findall(criterio_regex, criterioPesquisa)
            
            operador = '&' if '&' in criterioPesquisa else '|'

            responseLivros = self.database_service_stub.RequestAll(DatabaseService_pb2.TableMessage(tName="livros"))
            
            for responseLivro in responseLivros:
                livro = json.loads(responseLivro.value)
                condicoes = []
                
                for campo, valor in criterios:
                    if campo == 'isbn':
                        condicoes.append(valor.lower() in livro.get("isbn").lower())
                    elif campo == 'titulo':
                        condicoes.append(valor.lower() in livro.get("titulo").lower())
                    elif campo == 'autor':
                        condicoes.append(valor.lower() in livro.get("autor").lower())
                
                if (operador == '&' and all(condicoes)) or (operador == '|' and any(condicoes)):
                    yield PortalBiblioteca_pb2.Livro(isbn=livro.get("isbn"), titulo=livro.get("titulo"),
                        autor=livro.get("autor"), total=livro.get("total"), restante=livro.get("restante"))
        except grpc.RpcError:
            raise grpc.RpcError

def run_server(porta: int, portaDatabase: int) -> None:
    class_work = PortalBibliotecaServidor(portaDatabase)

    server = None

    try:
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        PortalBiblioteca_pb2_grpc.add_PortalBibliotecaServicer_to_server(class_work, server)
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
        porta = 99921

    run_server(porta, portaDatabase)