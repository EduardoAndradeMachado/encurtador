# 🔗 Encurtador de URLs

Projeto pessoal de um encurtador de URLs simples, desenvolvido em **Flask** e **SQLite**.  
Permite criar links curtos para URLs longas, acompanhar o número de acessos e recuperar links já encurtados.  
Este projeto está em **versão beta**.

## ✨ Funcionalidades

- **Encurtar URLs**: Gere um link curto exclusivo para qualquer URL.
- **Redirecionamento**: Acesse o link curto e seja redirecionado automaticamente para a URL original.
- **Contador de acessos**: Veja quantas vezes o link curto foi acessado.
- **Recuperação de link**: Recupere o link curto a partir da URL original.
- **Interface web**: Frontend simples e responsivo.

## 🚀 Como usar

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/EduardoAndradeMachado/encurtador-simples.git
   ```
2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Crie o banco de dados:**
Crie um arquivo database.db com a seguinte estrutura:

   ```sql
   CREATE TABLE urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    url_longa TEXT UNIQUE NOT NULL,
    clicks INTEGER DEFAULT 0
    );
   ```
4. **Execute o projeto:**
   ```bash
   python app.py
   ```

5. **Acesse no navegador:**
   http://localhost:5000

6. **Estrutura:**
   ```csharp
    .
    ├── app.py           # Código principal da aplicação Flask
    ├── templates/       # Páginas HTML
    ├── static/          # Arquivos estáticos (CSS, JS, imagens)
    └── database.db      # Banco de dados SQLite
   ```

## ⚠️ Observações
- Projeto em desenvolvimento (versão beta).
- Para uso local e fins de estudo.
- Sinta-se à vontade para sugerir melhorias ou reportar bugs.

