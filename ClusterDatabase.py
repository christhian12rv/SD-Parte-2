from pysyncobj import SyncObj, SyncObjConf, replicated
import plyvel
from cachetools import TTLCache
import atexit
import logging
logging.basicConfig(level=logging.DEBUG)

CACHE_TTL_SECONDS = 5  # Tempo de validade do cache em segundos

class ClusterDatabase(SyncObj):
    def __init__(self, self_address, partner_addresses, db_path):
        conf = SyncObjConf( connectionTimeout=10000, commandsQueueSize=10000, logLevel=logging.DEBUG)
        super().__init__(self_address, partner_addresses, conf=conf)
        
        # Inicializa LevelDB e cache
        self.db = plyvel.DB(db_path, create_if_missing=True)
        atexit.register(self.db.close)
        self.cache = TTLCache(maxsize=1000, ttl=CACHE_TTL_SECONDS)
        self.dbPath = db_path

    def close(self):
        self.db.close()

    # CREATE replicado
    @replicated
    def create(self, table, key, value):
        print("Create: ", table, key, type(value))
        full_key = f'{table}:{key}'.encode()
        self.db.put(full_key, value.encode())
        self.cache[full_key] = value

    # READ com cache
    def request(self, table, key):
        full_key = f'{table}:{key}'.encode()
        if full_key in self.cache:
            return self.cache[full_key]
        try:
            value = self.db.get(full_key)
            self.cache[full_key] = value
            return (value.decode('utf-8') if value is not None else value)
        except KeyError:
            return None
    
    # READ com cache
    def requestAll(self, table):
        result = list(self.db.iterator(prefix=table.encode('utf-8'), include_key=False))
        print(result)
        return [(value.decode('utf-8') if value is not None else value) for value in result]

    # UPDATE replicado
    @replicated
    def update(self, table, key, value):
        full_key = f'{table}:{key}'.encode()
        self.db.put(full_key, value.encode())
        self.cache[full_key] = value

    # DELETE replicado
    @replicated
    def delete(self, table, key):
        full_key = f'{table}:{key}'.encode()
        self.db.delete(full_key)
        if full_key in self.cache:
            del self.cache[full_key]

# Configurações dos clusters
def start_cluster(cluster_id, self_address, partner_addresses):
    db_path = f'./data_cluster{cluster_id}'
    cluster_db = ClusterDatabase(self_address, partner_addresses, db_path)

    print("Waiting for cluster to synchronize...")

    while not cluster_db.isReady():
        pass

    print("Cluster is ready")
    return cluster_db