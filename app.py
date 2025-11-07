import json
from flask import Flask, request, session, redirect, url_for, render_template, jsonify
import random
import string

app = Flask(__name__)
app.secret_key = 'your_secret_key'

users = {}
saved_passwords = {}

def load_data():
    global users, saved_passwords
    try:
        with open('users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
    except:
        users = {}
    try:
        with open('saved_passwords.json', 'r', encoding='utf-8') as f:
            saved_passwords = json.load(f)
    except:
        saved_passwords = {}

def save_data():
    with open('users.json', 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)
    with open('saved_passwords.json', 'w', encoding='utf-8') as f:
        json.dump(saved_passwords, f, ensure_ascii=False, indent=4)


def create_password(length, uppercase, lowercase, numbers, special):
    chars = ''
    if uppercase:
        chars += string.ascii_uppercase
    if lowercase:
        chars += string.ascii_lowercase
    if numbers:
        chars += string.digits
    if special:
        chars += string.punctuation

    if not chars:
        chars = string.ascii_letters + string.digits + string.punctuation

    return ''.join(random.choice(chars) for _ in range(length))

#Авторизация
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return "Неверный логин или пароль", 401

    return render_template('login.html')

#Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return "Введите имя пользователя и пароль", 400
        if username in users:
            return "Пользователь уже существует", 400

        users[username] = password
        saved_passwords[username] = []
        save_data()
        session['username'] = username
        return redirect(url_for('home'))

    return render_template('register.html')

#Выход
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

#Главная страница
@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))

    user = session['username']
    user_passwords = saved_passwords.get(user, [])
    return render_template('index.html', passwords=user_passwords)


@app.route('/save_password', methods=['POST'])
def save_password():
    if 'username' not in session:
        return jsonify({'error': 'Вы не вошли в систему'}), 401

    data = request.get_json()
    site = data.get('site')
    login = data.get('login')
    password = data.get('password')

    if not site or not login or not password:
        return jsonify({'error': 'Заполните все поля'}), 400

    user = session['username']
    saved_passwords.setdefault(user, []).append({
        'site': site,
        'login': login,
        'password': password
    })
    save_data()
    return jsonify({'message': 'Данные сохранены!'})

#Генерация
@app.route('/generate', methods=['POST'])
def generate():
    if 'username' not in session:
        return jsonify({'error': 'Пользователь не авторизован'}), 401

    data = request.get_json()
    try:
        length = int(data.get('length', 12))
        if length < 4:
            length = 4
        elif length > 50:
            length = 50

        uppercase = data.get('uppercase', True)
        lowercase = data.get('lowercase', True)
        numbers = data.get('numbers', True)
        special = data.get('special', True)

        password = create_password(length, uppercase, lowercase, numbers, special)

        user = session['username']
        saved_passwords.setdefault(user, []).append({
            'site': 'generated_password',
            'login': '',
            'password': password
        })
        save_data()

        return jsonify({'password': password})

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    load_data()
    app.run(debug=True, host='0.0.0.0', port=5000)
