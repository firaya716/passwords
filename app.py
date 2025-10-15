from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import random
import string
import json
import os

app = Flask(__name__)


def generate_password(length=12, use_uppercase=True, use_lowercase=True,
                      use_numbers=True, use_special=True):
    characters = ''

    if use_uppercase:
        characters += string.ascii_uppercase
    if use_lowercase:
        characters += string.ascii_lowercase
    if use_numbers:
        characters += string.digits
    if use_special:
        characters += '!@#$%^&*()_+-=[]{}|;:,.<>?'

    if not characters:
        characters = string.ascii_letters + string.digits

    password = ''.join(random.choice(characters) for _ in range(length))
    return password


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

    pwd = ''.join(random.choice(chars) for _ in range(length))
    return pwd


@app.route('/')
def index():
    def home():
        return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    try:
        data = request.get_json()
        length = int(data.get('length', 12))
        use_uppercase = data.get('uppercase', True)
        use_lowercase = data.get('lowercase', True)
        use_numbers = data.get('numbers', True)
        use_special = data.get('special', True)

        # Валидация длины
        if length < 4:
            length = 4
        elif length > 50:
            length = 50

        password = generate_password(
            length=length,
            use_uppercase=use_uppercase,
            use_lowercase=use_lowercase,
            use_numbers=use_numbers,
            use_special=use_special
        )

        # настройки
        uppercase = data.get('uppercase', True)
        lowercase = data.get('lowercase', True)
        numbers = data.get('numbers', True)
        special = data.get('special', True)

        password = create_password(length, uppercase, lowercase, numbers, special)
        return jsonify({'password': password})


    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', post = 5000)
