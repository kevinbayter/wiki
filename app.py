from flask import Flask, render_template, request, redirect, jsonify, session, flash
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os
import sqlite3

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'unasecretkeymuysecreta'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    con = sqlite3.connect("comments.db")
    cur = con.cursor()
    cur.execute("""SELECT c.comment_id, c.comment, u.name, u.profile_picture 
               FROM comments c 
               INNER JOIN users u ON c.user_id = u.user_id""")
    comments = cur.fetchall()
    con.close()
    return render_template('index.html', comments=comments)

@app.route('/add-comment', methods=['POST'])
def add_comment():
    commentData = request.json
    comment = commentData.get('comment')
    parent_comment_id = commentData.get('parent_comment_id')
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify(success=False, message="Debes iniciar sesión para comentar")

    con = sqlite3.connect("comments.db")
    cur = con.cursor()

    if parent_comment_id:
        cur.execute("INSERT INTO comments (comment, user_id, parent_comment_id) VALUES (?, ?, ?)", (comment, user_id, parent_comment_id))
    else:
        cur.execute("INSERT INTO comments (comment, user_id) VALUES (?, ?)", (comment, user_id))
    
    cur.execute("SELECT name FROM users WHERE user_id = ?", (user_id,))
    username = cur.fetchone()[0]
    con.commit()
    con.close()
    return jsonify(success=True, username=username)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        file = request.files.get('profile_picture')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = "default_avatar.png"
        
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

        try:
            con = sqlite3.connect("comments.db")
            cur = con.cursor()
            cur.execute("INSERT INTO users (name, username, password, profile_picture) VALUES (?, ?, ?, ?)", (name, username, hashed_pw, filename))
            con.commit()
            con.close()
            flash('Registro exitoso. Por favor, inicia sesión.', 'success')
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash('El nombre de usuario ya está en uso. Por favor, elige otro.', 'danger')
            return redirect('/register')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        con = sqlite3.connect("comments.db")
        cur = con.cursor()
        cur.execute("SELECT user_id, name, password, profile_picture FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        con.close()

        if user and bcrypt.check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['profile_picture'] = user[3]  # Store the profile picture in session
            flash('Inicio de sesión exitoso!', 'success')
            return redirect('/')
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
            return redirect('/login')
    return render_template('login.html')

@app.route('/delete-comment/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify(success=False, message="Debes iniciar sesión para eliminar comentarios")

    con = sqlite3.connect("comments.db")
    cur = con.cursor()

    cur.execute("DELETE FROM comments WHERE comment_id = ? AND user_id = ?", (comment_id, user_id))
    
    con.commit()
    con.close()
    return jsonify(success=True)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('profile_picture', None)  # Clear the profile picture from session
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
