from urllib.parse import urlparse, urlunparse
import random
import string
import sqlite3
import re
from flask import Flask, redirect, render_template, request, url_for, jsonify
from device_detector import DeviceDetector
import json

# Configuração da aplicação Flask
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

def get_connection():
    """
    Cria e retorna uma conexão com o banco de dados SQLite.
    Define o row_factory para acessar colunas por nome.
    """
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def gerar_slug():
    """
    Gera uma string aleatória de 5 caracteres (letras e números) para ser usada como slug.
    """
    tamanho_slug = 5
    return ''.join(random.choices(string.ascii_letters + string.digits, k=tamanho_slug))

def valida_normaliza_url(received_url):
    # 1) Checa se veio algo e remove espaços em branco (incluindo tabs e quebras de linha)
    if not received_url:
        return None
    received_url = re.sub(r"\s+", "", received_url)

     # 2) Se não tiver esquema, adiciona https://
    if not received_url.startswith(('http://', 'https://')):
        received_url = 'https://' + received_url
    
    # 3) Faz o parsing (quebra em pedaços)
    parsed = urlparse(received_url)

    # 4) Verifica se o esquema é http ou https e se há netloc (domínio)
    if parsed.scheme.lower() not in ("http", "https") or not parsed.netloc:
        return None
    
    # 5) Força o netloc todo em minúsculas
    domain = parsed.netloc.lower()

    #6 Verifica se o domínio é válido:
    padrao = r"^(?=.{1,253}$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}$"
    if not re.match(padrao, domain):
        return None

    # 7) Reconstrói a URL sem alterar path/query/fragment
    url_normalizada = urlunparse((
        parsed.scheme.lower(),
        domain,
        parsed.path or "",
        parsed.params,
        parsed.query,
        parsed.fragment
    ))
    
    return url_normalizada

def get_slug_from_long_url(url_longa):
    """
    Busca no banco de dados a slug correspondente a uma URL longa.
    Retorna a slug ou None se não encontrada.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT slug FROM urls WHERE url_longa = ?;", (url_longa,))
        slug = cursor.fetchone()
        if slug:
            slug = slug['slug']
        else:
            slug = None
    except Exception as e:
        slug = None
    finally:
        if conn:
            conn.close()

    return slug

@app.errorhandler(500)
def erro_interno(error):
    """
    Handler para erros 500 (erro interno do servidor).
    """
    return render_error("Erro interno no servidor.", 500)

def render_error(message, codigo):
    """
    Renderiza a página de erro com a mensagem e código HTTP especificados.
    """
    return render_template("error.html", error=message), codigo


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Rota principal:
    - GET: exibe o formulário para encurtar URL
    - POST: processa a URL enviada, gera slug única e salva no banco
    """
    if request.method == "POST":
        option_custom_url = request.form.get("select-custom-url")
        option_expiration_date = request.form.get("select-date")
        # Valida e normaliza a URL recebida do formulário
        formated_url = valida_normaliza_url(request.form.get("url"))
        if not formated_url:
            return render_error("A URL digitada é inválida.", 400)

        # Tenta gerar uma slug única até 10 vezes
        for _ in range(10):
            conn = None
            try:
                if option_custom_url == 'on':
                    short_slug = request.form.get("custom-url")
                    if not short_slug:
                        return render_error("URL customizada não informada.", 400)
                    
                    if re.search(r'[^a-z0-9-]', short_slug):
                        return render_error("Caracter inválido na url.", 400)
                    
                    if len(short_slug) > 24:
                        return render_error("Slug escolhida é muito longa.", 400)
                    # Adicionar após front ser aprimorado.
                    # if not short_slug.startswith(request.url_root):
                    #     return render_error("URL customizada informada é inválida.", 400)
                else:
                    short_slug = gerar_slug()

                conn = get_connection()
                cursor = conn.cursor()
                
                query = """
                    INSERT INTO urls (slug, url_longa)
                    VALUES (?, ?);
                """
                cursor.execute(query, (short_slug, formated_url))
                conn.commit()

            except sqlite3.IntegrityError as e:
                # Trata erros de unicidade (slug ou url_longa já existem)
                error_message = str(e).lower()
                if "slug" in error_message:
                    print('Slug já existe, gerando uma nova...')
                    continue  # Tenta novamente com outra slug
                elif "url_longa" in error_message:
                    # URL já cadastrada, busca a slug existente
                    short_slug = get_slug_from_long_url(formated_url)
                    if not short_slug:
                        return render_error("Erro interno no servidor.", 500)
                    # Sucesso sai do loop
                    break
                else:
                    return render_error("Erro interno no servidor.", 500)                    
                
            except Exception as e:
                # Outros erros inesperados
                return render_error("Erro interno no servidor.", 500)
            
            else:
                # Sucesso ao inserir, sai do loop
                break

            finally:
                if conn:
                    conn.close()
        else:
            # Não conseguiu gerar uma slug única após 10 tentativas
            return render_error("Não foi possível gerar uma URL curta única, tente novamente.", 500)

        # Redireciona para a página de resultado com a slug gerada
        return redirect(f"/resultado?short_slug={short_slug}")
    else:
        # GET: exibe o formulário
        return render_template("index.html")


@app.route("/resultado", methods=["GET"])
def resultado():
    """
    Exibe o resultado da criação ou recuperação de uma URL curta.
    Mostra a URL curta e o número de cliques.
    """
    slug = request.args.get('short_slug')

    if not slug:
        return redirect("/")

    short_url = url_for('redirecionamento', slug=slug, _external=True)

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT clicks FROM urls WHERE slug = ?;", (slug,))
        clicks = cursor.fetchone()
        if clicks:
            clicks = clicks['clicks']
        else:
            return render_error("A url digitada não foi encontrada.", 400)
    except Exception as e:
        return render_error("Erro interno no servidor.", 500)
    finally:
        if conn:
            conn.close()

    return render_template("resultado.html", short_url=short_url, clicks=clicks)


@app.route("/recuperar", methods=["GET", "POST"], strict_slashes=False)
def recuperar():
    """
    Permite ao usuário recuperar a slug de uma URL longa já cadastrada.
    """
    if request.method == "POST":
        formated_url = valida_normaliza_url(request.form.get("url"))
        if not formated_url:
            return render_error("A URL digitada é inválida.", 400)
    
        short_slug = get_slug_from_long_url(formated_url)
        if not short_slug:
            return render_error("A URL digitada não foi encontrada.", 400)

        return redirect(f"/resultado?short_slug={short_slug}")
    
    return render_template("recuperar.html")

@app.route("/log", methods=["GET", "POST"], strict_slashes=False)
def log():
    """
    Rota para gerenciar logs de acesso:
    - POST: Adiciona dados do usuário no log
    - GET: Recupera histórico de acessos detalhado com base na slug
    """
    if request.method == "POST":
        """
        Adiciona dados do usuário no log
        """
        try: 
            dados = json.loads(request.data.decode('utf-8'))
        except:
            return jsonify({"status": "error",
                            "message": "Entrada inválida."}), 401

        url_id = dados.get('url_id')
        user_agent = dados.get('user_agent')
        largura_tela = dados.get('largura_tela')
        altura_tela = dados.get('altura_tela')
        idioma = dados.get('idioma')
        ip = request.remote_addr
        dispositivo = None

        if not url_id:
            return jsonify({"status": "error",
                            "message": "url_id não informada"}), 400
        
        if user_agent:
            dispositivo = DeviceDetector(user_agent).parse()
            dispositivo = f"{dispositivo.device_type()} - {dispositivo.os_name()}"

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Valida se o id existe na lista de urls
            cursor.execute("SELECT slug FROM urls WHERE id = ?;", (url_id,))
            if not cursor.fetchone():
                return jsonify({"status": "error",
                            "message": "Slug não encontrada."}), 404

            # Inserir dados
            query = """
                INSERT INTO logs (url_id, ip, user_agent, largura_tela, altura_tela, idioma, dispositivo)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """
            cursor.execute(query, (url_id, ip, user_agent, largura_tela, altura_tela, idioma, dispositivo))
            conn.commit()
        except:
            return jsonify({"status": "error",
                            "message": "Erro interno no servidor."}), 500
        finally:
            if conn:
                conn.close()
        return jsonify({"status": "ok"}), 200
    elif request.method == "GET":
        """
        Encontra o id com base na slug, em seguida puxa o histórico de acessos detalhado.
        """
        short_slug = request.args.get('short_slug')
        if not short_slug:
            return jsonify({"status": "error",
                            "message": "Slug curta não informada"}), 400

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM urls WHERE slug = ?;", (short_slug, ))
            url_id = cursor.fetchone()
            if not url_id:
                return jsonify({"status": "error",
                                "message": "ID não encontrado"}), 404
            else:
                url_id = url_id['id']

            cursor.execute("SELECT * FROM logs WHERE url_id = ? ORDER BY date DESC;", (url_id, ))
            logs = cursor.fetchall()
            if not logs:
                return jsonify({"status": "error",
                                "message": "Logs não encontrados"}), 404
            
            logs_dict = []
            for log in logs:
                logs_dict.append({
                    "ip": log["ip"],
                    "user_agent": log["user_agent"],
                    "largura_tela": log["largura_tela"],
                    "altura_tela": log["altura_tela"],
                    "idioma": log["idioma"],
                    "localidade": log["localidade"],
                    "date": log["date"],
                    "dispositivo": log["dispositivo"]
                })

            # logs_dict = [dict(log) for log in logs] # Retorna todas colunas (pode vir a ser util)
        except:
            return jsonify({"status": "error",
                            "message": "Erro interno no servidor."}), 500
        finally:
            if conn:
                conn.close()
        return jsonify(logs_dict), 200


@app.route("/<slug>", methods=["GET"], strict_slashes=False)
def redirecionamento(slug):
    """
    Rota de redirecionamento:
    - Busca a URL longa correspondente à slug
    - Incrementa o contador de cliques
    - Redireciona o usuário para a URL longa
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT url_longa, id FROM urls WHERE slug = ?;", (slug,))
        data_recive = cursor.fetchone()
        if data_recive:
            url_longa = data_recive['url_longa']
            url_id = data_recive['id']
            # Incrementa o contador de cliques
            cursor.execute("UPDATE urls SET clicks = clicks + 1 WHERE slug = ?;", (slug,))
            conn.commit()
        else:
            return render_error("Página não encontrada.", 404)
    except Exception as e:
        return render_error("Erro interno no servidor.", 500)
    finally:
        if conn:
            conn.close()

    return render_template("redirect.html", url=url_longa, url_id=url_id)


if __name__ == "__main__":
    # Inicia o servidor Flask em modo debug
    app.run(debug=True)
