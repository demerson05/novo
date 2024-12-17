from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('.venv', 'static', 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['SECRET_KEY'] = 'supersecretkey'  # Necessário para sessões e flash messages

# Simulação de "banco de dados"
users = {}
posts = {}

# Garante que o diretório de uploads existe
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Função para verificar se o usuário está autenticado
def is_authenticated():
    return 'user' in session

@app.route('/')
def index():
    return render_template('index.html', posts=posts, authenticated=is_authenticated())

@app.route('/post/<int:post_id>')
def post(post_id):
    post = posts.get(post_id)
    return render_template('post.html', post=post)

@app.route('/new', methods=['GET', 'POST'])
def new_post():
    if not is_authenticated():
        flash("Você precisa estar logado para criar uma postagem.", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        
        file = request.files.get('image')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = url_for('static', filename=f'uploads/{filename}')
        else:
            image_url = ''  # Se não houver imagem ou a extensão não for permitida
        
        post_id = len(posts) + 1
        posts[post_id] = {'title': title, 'body': body, 'image_url': image_url}
        flash("Postagem criada com sucesso!", "success")
        return redirect(url_for('index'))

    return render_template('new_post.html')

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if not is_authenticated():
        flash("Você precisa estar logado para editar uma postagem.", "error")
        return redirect(url_for('login'))

    post = posts.get(post_id)
    if request.method == 'POST':
        post['title'] = request.form['title']
        post['body'] = request.form['body']
        
        file = request.files.get('image')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            post['image_url'] = url_for('static', filename=f'uploads/{filename}')
        
        flash("Postagem editada com sucesso!", "success")
        return redirect(url_for('index'))
    return render_template('edit_post.html', post=post, post_id=post_id)

@app.route('/delete/<int:post_id>')
def delete_post(post_id):
    if not is_authenticated():
        flash("Você precisa estar logado para excluir uma postagem.", "error")
        return redirect(url_for('login'))

    posts.pop(post_id, None)
    flash("Postagem excluída com sucesso.", "success")
    return redirect(url_for('index'))

# Rotas de autenticação
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users.get(username)
        if user and check_password_hash(user['password'], password):
            session['user'] = username
            flash(f"Bem-vindo, {username}!", "success")
            return redirect(url_for('index'))
        else:
            flash("Nome de usuário ou senha incorretos.", "error")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if username in users:
            flash("Este nome de usuário já está em uso.", "error")
        elif password != confirm_password:
            flash("As senhas não correspondem.", "error")
        else:
            users[username] = {'password': generate_password_hash(password)}
            flash("Usuário registrado com sucesso! Faça login.", "success")
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Você saiu da conta.", "info")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
