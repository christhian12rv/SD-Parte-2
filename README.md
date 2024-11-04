<h1>Projeto 1 de Sistemas Distribuídos</h1>

### Membros do Grupo

- Christhian Rezende Vieira           - 12111BCC028
- Chrystopher Pinter Oliveira Lacerda - 12111BCC027
- Eduardo Alvares Cipriano            - 12011BCC049
- Natan Gonçalves de Lyra             - 12111BCC006

### Requisitos Básicos

- Implementar os casos de uso usando tabelas hash locais aos servidores, em memória (hash tables, dicionários, mapas, etc).
- Documentar o esquema de dados usados nas tabelas e escolhas para cada JSON.
- Suportar a execução de múltiplos clientes e servidores.
- Implementar os clientes e servidores com interface de linha de comando para execução.
- Certificar-se de que todas as APIs possam retornar erros/exceções e que estas são tratadas, explicando sua decisão de tratamento dos erros.
- Implementar a propagação de informação entre as diversas caches do sistema usando necessariamente pub-sub, já que a comunicação é de 1 para muitos.
- Utilizar o broker pub-sub mosquitto com a configuração padrão e aceitando conexões na interface local (localhost ou 127.0.0.1), porta TCP 1883.
- Gravar um vídeo de no máximo 5 minutos demonstrando que os requisitos foram atendidos.

### Documentação do esquema de dados

Para usuários escolhemos estruturar o JSON da seguinte forma:

```bash
dados = {
        "cpf": cpf,
        "nome": nome
    }
```

Para livros escolhemos estruturar o JSON da seguinte forma:

```bash
dados = {
        "isbn": isbn,
        "titulo": titulo,
        "autor": autor,
        "total": total
    }
```

Para salvar os empréstimos realizados pelos usuários, decidimos estruturar um dicionário de <I>usuarioLivros</I> que salva a hora do empréstimo (para verificações futuras de Bloquear Usuário):

```bash
usuariosLivros[cpf] = { 'livros': [{'isbn': livro.isbn, 'dataEmprestimo': datetime.now()}]}
```

### Instruções de Compilação

Primeiramente faça o <I>git clone</I> do nosso repositório.

```bash
git clone https://github.com/NatanGLyra/Projeto01-SD.git
```

Logo em seguida instale todas as depêndencias necessárias para a execução do projeto:

```bash
cd Trabalho
chmod +x compile.sh
./compile.sh
```

### Abertura dos Servidores e Clientes

Antes de propriamente abrir os Servidores e clientes, deixe o mosquitto rodando em um terminal separado:

```bash
mosquitto
```

Para cada Servidor Administrativo execute essa linha substituido <I><B><PORTA_DESEJADA></B></I> com a porta para aquele servidor:

```bash
./cad-server.sh <PORTA_DESEJADA>
```

Para cada Servidor Biblioteca execute essa linha substituido <I><B><PORTA_DESEJADA></B></I> com a porta para aquele servidor:

```bash
./bib-server.sh <PORTA_DESEJADA>
```

Para cada Cliente Administrativo execute essa linha substituido <I><B><PORTA_DESEJADA></B></I> com a porta igual a de um servidor previamente inicializado:

```bash
./cad-client.sh <PORTA_DESEJADA>
```

Para cada Cliente Biblioteca execute essa linha substituido <I><B><PORTA_DESEJADA></B></I> com a porta igual a de um servidor previamente inicializado:

```bash
./bib-client.sh <PORTA_DESEJADA>
```

### Utilização dos Clientes e Servidores

<B>Servidores</B>: Após executar as linhas de comando que inicializam os servidores, basta deixar o terminal aberto para que o servidor continue a funcionar.

<B>Clientes</B>: Após executar as linhas de comando que inicializam os clientes, basta selecionar uma operação apartir do menu impresso no terminal, onde a leitura será realizada a partir do teclado.

### Vídeo

<B>Link:</B> [Vídeo de Apresentação dos Requisitos](https://ufubr-my.sharepoint.com/:v:/g/personal/chrystopherpol_ufu_br/EUt-gjyTNIFOnMZUseIzo78B6p8Ag_C0zJ0mGAfZg5Ateg)
