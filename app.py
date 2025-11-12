from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Замените на ваш секретный ключ

DATABASE = 'data.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS saved_passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            site TEXT NOT NULL,
            login TEXT NOT NULL,
            password TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']

    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT site, login, password FROM saved_passwords WHERE user_id = ?', (user_id,))
    passwords = c.fetchall()
    conn.close()

    return render_template('index.html', passwords=passwords)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        if not username or not password:
            flash('Пожалуйста, заполните все поля')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        conn = get_db()
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            flash('Регистрация прошла успешно! Войдите в систему.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Пользователь с таким именем уже существует!')
            return redirect(url_for('register'))
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT id, password FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = username
            flash('Успешный вход')
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы')
    return redirect(url_for('login'))

@app.route('/save_password', methods=['POST'])
def save_password():
    if 'user_id' not in session:
        flash('Требуется вход в систему')
        return redirect(url_for('login'))

    site = request.form['site'].strip()
    login_ = request.form['login'].strip()
    password = request.form['password'].strip()

    if not site or not login_ or not password:
        flash ('Заполните все поля')
        return redirect(url_for('index'))

    user_id = session['user_id']

    conn = get_db()
    c = conn.cursor()
    c.execute(
        'INSERT INTO saved_passwords (user_id, site, login, password) VALUES (?, ?, ?, ?)',
        (user_id, site, login_, password)
    )
    conn.commit()
    conn.close()

    flash('Пароль успешно сохранён')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
