import validators
import random
import string
import sqlite3
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
    short_slug = ''.join(random.choices(string.ascii_letters + string.digits, k=tamanho_slug))
    return short_slug

def formata_url(url):
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    if url.endswith('/'):
        url = url[:-1] 
    return url

def get_slug_from_log_url(url_longa):
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
        return render_template("error.html", error="Erro interno no servidor."), 500

    finally:
        if conn:
            conn.close()

    return slug

@app.errorhandler(500)
def erro_interno(error):
    return render_template("error.html", error="Erro interno no servidor."), 500

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        recived_url = request.form.get("url")
        if not recived_url:
            return render_template("error.html", error="Um campo não foi preenchido."), 400
        
        formated_url = formata_url(recived_url)

        if not validators.url(formated_url):
            return render_template("error.html", error="A url digitada é inválida"), 400

        while(True):
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
                    short_slug = get_slug_from_log_url(formated_url)
                    if not short_slug:
                        return render_template("error.html", error="Erro interno no servidor."), 500
                    break
                else:
                    return render_template("error.html", error="Erro interno no servidor."), 500
                
            except Exception as e:
                return render_template("error.html", error="Erro interno no servidor."), 500
            
            else:
                break

            finally:
                if conn:
                    conn.close()

        return redirect(f"/resultado?short_slug={short_slug}")
    else:
        return render_template("index.html")


@app.route("/resultado", methods=["GET"])
def resultado():
    slug = request.args.get('short_slug')

    if not slug:
        return redirect("/")

    short_url = url_for('redirecionamento', slug=slug, _external=True)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT clicks FROM urls WHERE slug = ?;", (slug,))
        clicks = cursor.fetchone()
        if clicks:
            clicks = clicks['clicks']
        else:
            return render_template("error.html", error="A url digitada não foi encontrada."), 400
        
    except Exception as e:
        return render_template("error.html", error="Erro interno no servidor."), 500

    finally:
        if conn:
            conn.close()

    return render_template("resultado.html", short_url=short_url, clicks=clicks)


@app.route("/recuperar", methods=["GET", "POST"])
def recuperar():
    if request.method == "POST":
        recived_url = request.form.get("url")
        if not recived_url:
            return render_template("error.html", error="Um campo não foi preenchido."), 400
        
        recived_url = formata_url(recived_url)

        if not validators.url(recived_url):
            return render_template("error.html", error="A url digitada é inválida."), 400
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT slug FROM urls WHERE url_longa = ?;", (recived_url,))
            short_slug = cursor.fetchone()
            if short_slug:
                short_slug = short_slug['slug']
            else:
                return render_template("error.html", error="A URL digitada é inválida."), 400
            
        except Exception as e:
            return render_template("error.html", error="Erro interno no servidor."), 500

        finally:
            if conn:
                conn.close()

        return redirect(f"/resultado?short_slug={short_slug}")
    
    return render_template("recuperar.html")


@app.route("/<slug>", methods=["GET"], strict_slashes=False)
def redirecionamento(slug):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT url_longa FROM urls WHERE slug = ?;", (slug,))
        url_longa = cursor.fetchone()
        if url_longa:
            url_longa = url_longa['url_longa']

            cursor.execute("UPDATE urls SET clicks = clicks + 1 WHERE slug = ?;", (slug,))
            conn.commit()
        else:
            return render_template("error.html", error="Página não encontrada."), 404
        
    except Exception as e:
        return render_template("error.html", error="Erro interno no servidor."), 500

    finally:
        if conn:
            conn.close()

    return redirect(url_longa)


if __name__ == "__main__":
    app.run(debug=True)
