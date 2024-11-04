from concurrent import futures
import grpc
import DatabaseService_pb2_grpc
import DatabaseService_pb2
import sys
import ClusterDatabase
import json

SECONDS_TO_BLOCK = 10

def dateDiffInSeconds(dt2, dt1):
    timedelta = dt2 - dt1
    return timedelta.days * 24 * 3600 + timedelta.seconds

class DatabaseService(DatabaseService_pb2_grpc.DatabaseServiceServicer):
    def __init__(self, cluster_usuarios, cluster_livros):
        self.clusters = {
            "usuarios": cluster_usuarios,
            "livros": cluster_livros
        }
        self.tables = {}

    def CreateTable(self, request, context):
        tName = request.tName

        if tName not in self.tables:
            self.tables[tName] = {}
            print(f"Tabela '{tName}' criada com sucesso.")
            return DatabaseService_pb2.Status(status=0, msg=f"Tabela '{tName}' criada com sucesso.")
        else:
            print(f"Tabela '{tName}' já existe.")
            return DatabaseService_pb2.Status(status=1, msg=f"Tabela '{tName}' já existe.")

    def DeleteTable(self, request, context):
        tName = request.tName

        if tName in self.tables:
            del self.tables[tName]
            print(f"Tabela '{tName}' excluída com sucesso.")
            return DatabaseService_pb2.Status(status=0, msg=f"Tabela '{tName}' excluída com sucesso.")
        else:
            print(f"Tabela '{tName}' não encontrada.")
            return DatabaseService_pb2.Status(status=1, msg=f"Tabela '{tName}' não encontrada.")

    def Create(self, request, context):
        tName, key, value = request.tName, request.key, request.value
        if tName not in self.tables:
            print(f"Tabela '{tName}' não existe.")
            return DatabaseService_pb2.Status(status=1, msg=f"Tabela '{tName}' não existe.")
        
        cluster = self.select_cluster(tName)
        if cluster:
            cluster.create(tName, key, value)
            print(f"Entrada criada: {tName} -> {key} = {value}")
            return DatabaseService_pb2.Status(status=0, msg=f"Entrada criada: {tName} -> {key} = {value}")
            
        return DatabaseService_pb2.Status(status=1, msg=f"Houve um erro ao criar entrada")

    def Request(self, request, context):
        tName, key = request.tName, request.key
        if tName not in self.tables:
            print(f"Tabela '{tName}' não existe.")
            return DatabaseService_pb2.RequestReturn(value="None")

        cluster = self.select_cluster(tName)
        if cluster:
            value = cluster.request(tName, key)
            print(f"Consulta: {tName} -> {key} = {value}")
            
            if (value == None):
                return DatabaseService_pb2.RequestReturn(value="None")
            
            return DatabaseService_pb2.RequestReturn(value=value)
        return DatabaseService_pb2.RequestReturn(value="None")
    
    def RequestAll(self, request, context):
        tName = request.tName
        if tName not in self.tables:
            print(f"Tabela '{tName}' não existe.")
            return DatabaseService_pb2.RequestReturn(value="None")

        cluster = self.select_cluster(tName)
        if cluster:
            values = cluster.requestAll(tName)
            print(f"Consulta por todos: {tName} = Total: {len(values)}")
            
            if (values == None):
                return DatabaseService_pb2.RequestReturn(value="None")
            
            for value in values:
                yield DatabaseService_pb2.RequestReturn(value=value)
        return DatabaseService_pb2.RequestReturn(value="None")

    def Update(self, request, context):
        tName, key, value = request.tName, request.key, request.value

        if tName not in self.tables:
            print(f"Tabela '{tName}' não existe.")
            return DatabaseService_pb2.Status(status=1, msg=f"Tabela '{tName}' não existe.")

        cluster = self.select_cluster(tName)
        if cluster:
            cluster.update(tName, key, value)
            print(f"Entrada atualizada: {tName} -> {key} = {value}")
            return DatabaseService_pb2.Status(status=0, msg=f"Dado '{key}' atualizado com sucesso na tabela {tName}!")

        return DatabaseService_pb2.Status(status=1, msg=f"Houve um erro ao atualizar dado.")

    def Delete(self, request, context):
        tName, key = request.tName, request.key
        if tName not in self.tables:
            print(f"Tabela '{tName}' não existe.")
            return DatabaseService_pb2.Status(status=1, msg=f"Tabela '{tName}' não existe.")

        cluster = self.select_cluster(tName)
        if cluster:
            cluster.delete(tName, key)
            print(f"Entrada excluída: {tName} -> {key}")
            return DatabaseService_pb2.Status(status=0, msg=f"Dado '{key}' excluido com sucesso na tabela {tName}!")
        return DatabaseService_pb2.Status(status=1, msg=f"Houve um erro ao excluir dado")

    def select_cluster(self, tName):
        if tName in ["usuarios", "usuariosLivros"]:
            return self.clusters["usuarios"]
        elif tName == "livros":
            return self.clusters["livros"]
        else:
            print(f"Cluster para '{tName}' não encontrado.")
        return None

def run_server(porta: int) -> None:
    try:
        userPorts = ['3333', '4444', '5555']
        userPortChosen = sys.argv[2]
        userPorts.remove(userPortChosen)

        bookPorts = ['6666', '7777', '8888']
        bookPortChosen = sys.argv[3]
        bookPorts.remove(bookPortChosen)

        print(f"Iniciando cluster usuários na porta {userPortChosen}. Outras portas: {userPorts}")

        self_address_cluster0 = f'localhost:{userPortChosen}'
        partner_addresses_cluster0 = [f'localhost:{userPorts[0]}', f'localhost:{userPorts[1]}']
        cluster_usuarios = ClusterDatabase.start_cluster(userPortChosen, self_address_cluster0, partner_addresses_cluster0)

        print(f"Iniciando cluster livros na porta {bookPortChosen}. Outras portas: {bookPorts}")

        self_address_cluster1 = f'localhost:{bookPortChosen}'
        partner_addresses_cluster1 = [f'localhost:{bookPorts[0]}', f'localhost:{bookPorts[1]}']
        cluster_livros = ClusterDatabase.start_cluster(bookPortChosen, self_address_cluster1, partner_addresses_cluster1)
    
        class_work = DatabaseService(cluster_usuarios, cluster_livros)
        
        server = None
        
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        DatabaseService_pb2_grpc.add_DatabaseServiceServicer_to_server(class_work, server)
        server.add_insecure_port(f'localhost:{porta}')
    except grpc.RpcError as e:
        print(f'Error during gRPC startup: {e}')

    server.start()

    print('Server listening on port ' + str(porta) + '...')

    server.wait_for_termination()

if __name__ == '__main__':
    try:
        porta = int(sys.argv[1])
    except Exception:
        porta = 99929

    run_server(porta)