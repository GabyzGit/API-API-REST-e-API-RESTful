"""
Executar:
    python api_comparativa.py

O servidor inicia em http://localhost:8000. Exemplos:
    GET  http://localhost:8000/rpc/listar-livros
    POST http://localhost:8000/rpc/criar-livro
         JSON: {"titulo": "A cidade e as serras", "autor": "Eca de Queiros"}
    GET  http://localhost:8000/api/livros
    POST http://localhost:8000/api/livros
         JSON: {"titulo": "O alienista", "autor": "Machado de Assis"}
    GET  http://localhost:8000/restful/livros

Para criar ou atualizar um livro, envie Content-Type: application/json.
Os dados ficam em memoria e voltam ao exemplo inicial ao reiniciar o servidor.
"""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse


HOST = "localhost"
PORT = 8000
LIVROS = [
    {"id": 1, "titulo": "Dom Casmurro", "autor": "Machado de Assis"},
    {"id": 2, "titulo": "O Cortico", "autor": "Aluisio Azevedo"},
]
PROXIMO_ID = 3


def criar_livro(dados):
    global PROXIMO_ID
    titulo = dados.get("titulo")
    autor = dados.get("autor")
    if not isinstance(titulo, str) or not titulo.strip():
        raise ValueError("O campo 'titulo' e obrigatorio.")
    if not isinstance(autor, str) or not autor.strip():
        raise ValueError("O campo 'autor' e obrigatorio.")

    livro = {
        "id": PROXIMO_ID,
        "titulo": titulo.strip(),
        "autor": autor.strip(),
    }
    PROXIMO_ID += 1
    LIVROS.append(livro)
    return livro


class APIHandler(BaseHTTPRequestHandler):
    def send_json(self, status, dados=None, headers=None):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        for nome, valor in (headers or {}).items():
            self.send_header(nome, valor)
        self.end_headers()
        if dados is not None:
            corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
            self.wfile.write(corpo)

    def ler_json(self):
        tamanho = int(self.headers.get("Content-Length", "0"))
        corpo = self.rfile.read(tamanho)
        if not corpo:
            return {}
        try:
            dados = json.loads(corpo.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as erro:
            raise ValueError("Envie um JSON valido.") from erro
        if not isinstance(dados, dict):
            raise ValueError("O corpo JSON deve ser um objeto.")
        return dados

    def erro(self, status, mensagem):
        self.send_json(status, {"erro": mensagem})

    def do_GET(self):
        caminho = urlparse(self.path).path.rstrip("/") or "/"
        if caminho == "/rpc/listar-livros":
            self.send_json(200, {"resultado": LIVROS})
            return
        if caminho == "/api/livros":
            self.send_json(200, LIVROS)
            return
        if caminho == "/restful/livros":
            self.responder_colecao_restful()
            return
        self.responder_livro_individual("GET", caminho)

    def do_POST(self):
        caminho = urlparse(self.path).path.rstrip("/") or "/"
        try:
            dados = self.ler_json()
            if caminho == "/rpc/criar-livro":
                livro = criar_livro(dados)
                self.send_json(200, {"mensagem": "Livro criado.", "livro": livro})
                return
            if caminho in ("/api/livros", "/restful/livros"):
                livro = criar_livro(dados)
                restful = caminho.startswith("/restful/")
                if restful:
                    self.send_json(
                        201,
                        self.com_links(livro),
                        {"Location": f"/restful/livros/{livro['id']}"},
                    )
                else:
                    self.send_json(201, livro)
                return
            self.erro(404, "Rota nao encontrada.")
        except ValueError as erro:
            self.erro(400, str(erro))

    def do_PUT(self):
        caminho = urlparse(self.path).path.rstrip("/")
        if caminho.startswith("/rpc/"):
            self.erro(404, "Funcao RPC nao encontrada.")
            return
        try:
            dados = self.ler_json()
            self.atualizar_livro(caminho, dados)
        except ValueError as erro:
            self.erro(400, str(erro))

    def do_DELETE(self):
        caminho = urlparse(self.path).path.rstrip("/")
        if caminho == "/rpc/remover-livro":
            try:
                dados = self.ler_json()
                livro_id = int(dados.get("id", ""))
            except (ValueError, TypeError):
                self.erro(400, "Informe um 'id' numerico no JSON.")
                return
            livro = self.buscar_livro(livro_id)
            if livro is None:
                self.send_json(200, {"mensagem": "Livro nao encontrado."})
                return
            LIVROS.remove(livro)
            self.send_json(200, {"mensagem": "Livro removido."})
            return

        restful = caminho.startswith("/restful/")
        prefixo = "/restful/livros/" if restful else "/api/livros/"
        livro_id = self.id_da_rota(caminho, prefixo)
        if livro_id is None:
            self.erro(404, "Rota nao encontrada.")
            return
        livro = self.buscar_livro(livro_id)
        if livro is None:
            self.erro(404, "Livro nao encontrado.")
            return
        LIVROS.remove(livro)
        if restful:
            self.send_json(204)
        else:
            self.send_json(200, {"mensagem": "Livro removido."})

    def responder_livro_individual(self, metodo, caminho):
        if caminho.startswith("/api/livros/"):
            prefixo = "/api/livros/"
            restful = False
        elif caminho.startswith("/restful/livros/"):
            prefixo = "/restful/livros/"
            restful = True
        else:
            self.erro(404, "Rota nao encontrada.")
            return

        livro_id = self.id_da_rota(caminho, prefixo)
        if livro_id is None:
            self.erro(404, "Rota nao encontrada.")
            return
        livro = self.buscar_livro(livro_id)
        if livro is None:
            self.erro(404, "Livro nao encontrado.")
            return
        if restful:
            self.send_json(200, self.com_links(livro))
        else:
            self.send_json(200, livro)

    def atualizar_livro(self, caminho, dados):
        if caminho.startswith("/restful/livros/"):
            prefixo = "/restful/livros/"
            restful = True
        elif caminho.startswith("/api/livros/"):
            prefixo = "/api/livros/"
            restful = False
        else:
            self.erro(404, "Rota nao encontrada.")
            return
        livro_id = self.id_da_rota(caminho, prefixo)
        if livro_id is None:
            self.erro(404, "Rota nao encontrada.")
            return
        livro = self.buscar_livro(livro_id)
        if livro is None:
            self.erro(404, "Livro nao encontrado.")
            return
        try:
            titulo = dados.get("titulo")
            autor = dados.get("autor")
            if not isinstance(titulo, str) or not titulo.strip():
                raise ValueError("O campo 'titulo' e obrigatorio.")
            if not isinstance(autor, str) or not autor.strip():
                raise ValueError("O campo 'autor' e obrigatorio.")
        except ValueError as erro:
            self.erro(400, str(erro))
            return
        livro.update({"titulo": titulo.strip(), "autor": autor.strip()})
        if restful:
            self.send_json(200, self.com_links(livro))
        else:
            self.send_json(200, livro)

    def responder_colecao_restful(self):
        self.send_json(
            200,
            {
                "dados": [self.com_links(livro) for livro in LIVROS],
                "_links": {
                    "self": {"href": "/restful/livros"},
                    "criar": {
                        "href": "/restful/livros",
                        "metodo": "POST",
                    },
                },
            },
            {"Cache-Control": "public, max-age=60"},
        )

    @staticmethod
    def com_links(livro):
        recurso = f"/restful/livros/{livro['id']}"
        return {
            **livro,
            "_links": {
                "self": {"href": recurso},
                "colecao": {"href": "/restful/livros"},
                "atualizar": {"href": recurso, "metodo": "PUT"},
                "remover": {"href": recurso, "metodo": "DELETE"},
            },
        }

    @staticmethod
    def id_da_rota(caminho, prefixo):
        parte_id = caminho[len(prefixo):]
        if not parte_id or "/" in parte_id:
            return None
        try:
            return int(parte_id)
        except ValueError:
            return None

    @staticmethod
    def buscar_livro(livro_id):
        return next((livro for livro in LIVROS if livro["id"] == livro_id), None)

    def log_message(self, formato, *args):
        print(f"{self.address_string()} - {formato % args}")


if __name__ == "__main__":
    servidor = HTTPServer((HOST, PORT), APIHandler)
    print(f"Servidor ativo em http://{HOST}:{PORT} (Ctrl+C para encerrar)")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        servidor.server_close()
