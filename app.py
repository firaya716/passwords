from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import random
import string
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

users = {
    'user': 'password'
}

passwordsfile = 'saved_passwords.json'

if os.path.exists(passwordsfile):
    with open(passwordsfile, 'r') as f:
        saved_passwords = json.load(f)
else:
    saved_passwords = {}

def save_passwords_to_file():
    with open(passwordsfile, 'w') as f:
        json.dump(saved_passwords, f)

def create_password(length=12, uppercase=True, lowercase=True, numbers=True, special=True):
    chars = ''
    if uppercase:
        chars += string.ascii_uppercase
    if lowercase:
        chars += string.ascii_lowercase
    if numbers:
        chars += string.digits
    if special:
        chars += '!@#$%^&*()_+-=[]{}|;:,.<>?'

    if not chars:
        chars = string.ascii_letters + string.digits

    password = ''.join(random.choice(chars) for _ in range(length))
    return password

# Главная страница
@app.route('/')
def home():
    if 'username' in session:
        user = session['username']
        passwords = saved_passwords.get(user, [])
        return render_template('index.html', username=user, passwords=passwords)
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users and users[username] == password:
            session['username'] = username
            if username not in saved_passwords:
                saved_passwords[username] = []
                save_passwords_to_file()
            return redirect(url_for('home'))
        else:
            return "Неверный логин или пароль", 401

    return render_template('login.html')  # Отображаем форму входа

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

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
        saved_passwords.setdefault(user, []).append(password)
        save_passwords_to_file()

        return jsonify({'password': password})

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
