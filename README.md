# Trabalho Prático: Comparativo de Maturidade entre API, API REST e API RESTful

Este repositório contém a implementação prática demonstrando a evolução de maturidade e padronização de arquiteturas web através de um sistema simples e funcional de **Gerenciamento de Produtos**.

---

## 📌 Visão Geral do Projeto

A diferença fundamental entre as abordagens está no nível de conformidade com os princípios da web e do protocolo HTTP:

- **API Simples (Estilo RPC / Sem Padrão):** Trata endpoints como chamadas de funções remotas. Usa verbos nas URLs e concentra operações apenas em `GET` ou `POST`.
- **API REST:** Organiza a comunicação em torno de recursos (substantivos no plural) e utiliza os verbos HTTP corretos (`GET`, `POST`, `PUT`, `DELETE`) transferindo dados em formato JSON.
- **API RESTful:** Aplica rigorosamente todas as restrições arquiteturais REST (Roy Fielding), incluindo códigos de status HTTP semânticos (ex: 201 Created, 204 No Content), comunicação totalmente *stateless* e navegação hipermídia via **HATEOAS**.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python / JavaScript (Node.js) / PHP *(ajuste para a linguagem utilizada)*
- **Framework:** Express / Flask / Fastify / Laravel *(ajuste conforme necessário)*
- **Formato de Dados:** JSON

---

## 🚀 Implementação e Endpoints

### 1. API Simples (Estilo RPC / Sem Padrão)

Foco em funcionalidade imediata sem aderência aos padrões HTTP.

| Método HTTP | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/obterProdutos` | Retorna a lista de produtos. |
| `POST` | `/cadastrarProduto` | Adiciona um novo produto. |
| `POST` | `/atualizarProduto?id=1` | Atualiza o produto via parâmetro/body. |
| `GET` | `/deletarProduto?id=1` | Deleta um produto via `GET`. |

* **Características:** Verbos embutidos na URL, respostas sempre com status `200 OK` (mesmo para erros internos) e uso inadequado de métodos HTTP.

---

### 2. API REST (Padronização por Recursos)

Mapeamento correto de recursos e verbos HTTP.

| Método HTTP | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/produtos` | Listar todos os produtos. |
| `GET` | `/produtos/:id` | Buscar produto específico por ID. |
| `POST` | `/produtos` | Criar um novo produto. |
| `PUT` | `/produtos/:id` | Atualizar dados do produto. |
| `DELETE` | `/produtos/:id` | Remover o produto. |

* **Características:** Substantivos no plural nas URLs, payloads exclusivamente em JSON e separação clara das ações via métodos HTTP.

---

### 3. API RESTful (Rigor Total + HATEOAS)

Implementação stateless avançada com status HTTP semânticos e links hipermídia integrados à resposta.

#### Exemplos de Resposta (HATEOAS)

**Consulta de Produto (`GET /api/v1/produtos/1`):**

```json
{
  "id": 1,
  "nome": "Teclado Mecânico",
  "preco": 250.00,
  "estoque": 15,
  "_links": {
    "self": { "rel": "self", "method": "GET", "href": "/api/v1/produtos/1" },
    "update": { "rel": "update", "method": "PUT", "href": "/api/v1/produtos/1" },
    "delete": { "rel": "delete", "method": "DELETE", "href": "/api/v1/produtos/1" },
    "collection": { "rel": "collection", "method": "GET", "href": "/api/v1/produtos" }
  }
}
