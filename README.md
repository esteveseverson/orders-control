# Documentação Orders API

Este projeto implementa uma API RESTful para gerenciamento de autenticação utilizando JWT, clientes, produtos e pedidos, utilizando FastAPI, SQLAlchemy, Alembic e etc.

## Sumário dos Componentes
```
1. main.py: Inicialização da aplicação e configuração global.
2. models/: Modelos ORM para usuários, clientes, produtos e pedidos.
3. routers/: Rotas (endpoints) organizadas por domínio (auth, clients, products, orders).
```

### main.py
Responsável por:
```
1. Inicializar a aplicação FastAPI.
2. Configurar CORS para aceitar requisições de qualquer origem.
3. Incluir os routers de autenticação, clientes, produtos e pedidos.

main.py
@app.get('/', status_code=HTTPStatus.OK)
def server_status():
    return {'status': 'online'}

Este endpoint serve para verificar se o servidor está ativo
```

### models/
#### /models/init.py:
    Cria um registro de tabelas (table_registry) para uso com SQLAlchemy

#### /models/auth_model.py
    Define o modelo User com campos: id, nome, email, senha, perfil (admin/normal), datas de criação e atualização.

    Enum UserProfile para perfis de usuário


#### /models/client_model.py

    Modelo Client com id, nome, email, CPF, datas de criação e atualização.

    Validação de unicidade para email e CPF

#### /models/products_model.py

    Modelo Product com id, nome, descrição, categoria, preço (em centavos), código de barras, quantidade, validade, imagem, datas de criação e atualização


#### /models/order_model.py

    Enum OrderStatus para status do pedido.

    Modelo Order com id, client_id, total, status, datas, e relação com itens do pedido.

    Modelo OrderItem para itens do pedido, com referências a pedido e produto, quantidade e preço unitário

### routers/

Cada arquivo em /routers define endpoints RESTful para um domínio.
#### /routers/auth_routes.py

    POST /auth/login: Login do usuário, retorna token JWT.

    POST /auth/register: Cadastro de usuário normal.

    POST /auth/register-admin: Cadastro de usuário admin.

    POST /auth/refresh-token: Gera novo token JWT para usuário autenticado.

Utiliza dependências para sessão de banco e autenticação, além de hashing de senha e validação de credenciais

#### /routers/client_routes.py

    GET /clients/: Lista clientes, com filtros opcionais por nome/email e paginação.

    POST /clients/: Cria cliente, valida CPF e unicidade de email/CPF.

    GET /clients/{client_id}: Retorna um cliente específico.

    PUT /clients/{client_id}: Atualiza dados do cliente, com validações.

    DELETE /clients/{client_id}: Remove cliente (apenas admin pode deletar).

Utiliza validação de CPF e verifica permissões de usuário

#### /routers/products_routes.py

    GET /products/: Lista produtos, com filtros por categoria, preço e disponibilidade.

    POST /products/: Cria produto, faz upload de imagem, valida dados e unicidade do código de barras.

    GET /products/{product_id}: Retorna um produto específico.

    PUT /products/{product_id}: Atualiza produto, valida dados e unicidade do código de barras.

    DELETE /products/{product_id}: Remove produto (apenas admin pode deletar).

Os preços são armazenados em centavos para evitar problemas de precisão com ponto flutuante

#### /routers/orders_routes.py

    GET /orders/: Lista pedidos, com filtros por id, cliente ou status.

    POST /orders/: Cria pedido, valida estoque dos produtos, desconta quantidades, calcula total.

    GET /orders/{order_id}: Retorna detalhes de um pedido.

    PUT /orders/{order_id}: Atualiza status do pedido.

    DELETE /orders/{order_id}: Remove pedido (apenas admin pode deletar).

Transações são usadas para garantir atomicidade na criação de pedidos, revertendo alterações em caso de erro


### Fluxo de Autenticação e Permissões

    JWT: Utilizado para autenticação em endpoints protegidos.

    Permissões: Algumas operações (ex: deletar clientes/produtos/pedidos) exigem perfil admin.

### Validações e Utilitários

    Validação de CPF: Implementada via utilitário importado.

    Validação de dados: Checa unicidade de campos críticos, formatos e restrições de negócio (ex: preços positivos, datas futuras).

### Resumo das Dependências

    FastAPI: Framework principal da API.

    SQLAlchemy: ORM para modelagem e persistência de dados.

    Cloudinary: Upload de imagens de produtos.

    Pydantic: Schemas para validação e serialização de dados (não detalhados aqui).

### Observações Gerais

    Todos os endpoints seguem convenções REST.

    As respostas utilizam status HTTP apropriados.

    O código está modularizado por domínio, facilitando manutenção e testes.

# Execução de Projeto
```
1. git clone https://github.com/esteveseverson/orders-control
2. cd order-control
3. crie um arquivo .env
4. adicione os parametros do banco de dados
5. adicione os parametros da autenticação
6. adicione os parametros do cloudinary
7. docker compose up --build

o servidor iniciará na porta 8000
e o banco de dados na porta 5432

```
