sudo apt install python3-pip
python3 -m pip install grpcio
python3 -m pip install grpcio-tools
python3 -m pip install cachetools
python3 -m pip install plyvel
python3 -m pip install pysyncobj
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. PortalAdministrativo.proto
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. PortalBiblioteca.proto
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. DatabaseService.proto