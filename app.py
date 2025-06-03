from urllib.parse import urlparse, urlunparse
import random
import string
import sqlite3
import re
from flask import Flask, redirect, render_template, request, url_for

# Configure application
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

def get_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def gerar_slug():
    tamanho_slug = 5
    # Gera 5 caracteres aleatórios contendo letras maiusculas, minusculas e numeros.
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
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Receber a slug com base na url longa
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
    return render_error("Erro interno no servidor.", 500)

def render_error(message, codigo):
    return render_template("error.html", error=message), codigo


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Valida de recebeu uma url, formata com http/https e verifica se é valida
        formated_url = valida_normaliza_url(request.form.get("url"))
        if not formated_url:
            return render_error("A URL digitada é inválida.", 400)

        # Tenta gerar uma slug única ate 10 vezes
        for _ in range(10):
            conn = None
            try:
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
                error_message = str(e).lower()
                if "slug" in error_message:
                    print('Slug já existe, gerando uma nova...')
                    continue
                elif "url_longa" in error_message:
                    short_slug = get_slug_from_long_url(formated_url)
                    if not short_slug:
                        return render_error("Erro interno no servidor.", 500)
                    break
                else:
                    return render_error("Erro interno no servidor.", 500)                    
                
            except Exception as e:
                return render_error("Erro interno no servidor.", 500)
            
            else:
                break

            finally:
                if conn:
                    conn.close()
        else:
            return render_error("Não foi possível gerar uma URL curta única.", 500)

        return redirect(f"/resultado?short_slug={short_slug}")
    else:
        return render_template("index.html")


@app.route("/resultado", methods=["GET"])
def resultado():
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


@app.route("/recuperar", methods=["GET", "POST"])
def recuperar():
    if request.method == "POST":
        # Valida de recebeu uma url, formata com http/https e verifica se é valida
        formated_url = valida_normaliza_url(request.form.get("url"))
        if not formated_url:
            return render_error("A URL digitada é inválida.", 400)
    
        # Busca no banco de dados a slug com base na url longa
        short_slug = get_slug_from_long_url(formated_url)
        if not short_slug:
            return render_error("A URL digitada não foi encontrada.", 400)

        return redirect(f"/resultado?short_slug={short_slug}")
    
    return render_template("recuperar.html")


@app.route("/<slug>", methods=["GET"], strict_slashes=False)
def redirecionamento(slug):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Puxa a url longa com base na slug
        cursor.execute("SELECT url_longa FROM urls WHERE slug = ?;", (slug,))
        url_longa = cursor.fetchone()
        if url_longa:
            url_longa = url_longa['url_longa']

            # Adicionar mais um click no histórico
            cursor.execute("UPDATE urls SET clicks = clicks + 1 WHERE slug = ?;", (slug,))
            conn.commit()
        else:
            return render_error("Página não encontrada.", 404)
        
    except Exception as e:
        return render_error("Erro interno no servidor.", 500)

    finally:
        if conn:
            conn.close()

    return redirect(url_longa)


if __name__ == "__main__":
    app.run(debug=True)
