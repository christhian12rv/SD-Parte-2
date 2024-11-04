#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Uso: $0 <porta_grpc> <id_replica_cluster_1> <id_replica_cluster_2>"
    echo "Exemplo: $0 1234 1 2"
    exit 1
fi

PORTA_GRPC=$1
ID_REPLICA_CLUSTER_1=$2
ID_REPLICA_CLUSTER_2=$3

USER_PORTS=(3333 4444 5555)

BOOK_PORTS=(6666 7777 8888)

# Executa o serviço gRPC usando o Python com as portas configuradas para o cluster
echo "Iniciando réplica $ID_REPLICA do cluster $NUM_CLUSTER na porta $PORT..."

python3 -u DatabaseService.py "$PORTA_GRPC" "${USER_PORTS[$ID_REPLICA_CLUSTER_1]}" "${BOOK_PORTS[$ID_REPLICA_CLUSTER_2]}"