from flask import session, render_template, request, redirect, url_for, Response, jsonify, make_response
import datetime
from models.auth_model import auth
from utilities.helper import login_required


def login():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            data = auth.login(username=username)
            if data == "no":
                response = jsonify({"message": "no"})
                return response
            elif password == data['password']:
                session.clear()
                session['username'] = username
                response = jsonify({"status": 200, "message": "success"})
                expire_date = datetime.datetime.utcnow()
                expire_date = expire_date + datetime.timedelta(days=10)
                response.set_cookie("username", username, expires=expire_date)
                return response
            else:
                response = jsonify({"message": "fail"})
                return response

    except Exception as error:
        return error

    return render_template('login.html')


def sign_up():
    try:
        if request.method == 'POST':
            name = request.form.get('name')
            username = request.form.get('username')
            password = request.form.get('password')
            email = request.form.get('email')
            result = auth.signup(
                name=name, username=username, password=password, email=email)

            if result == "User already Exits":
                response = jsonify({"message": "fail"})
            else:
                response = jsonify({"status": 200, "message": "success"})
            return response
    except Exception as error:
        return error

    return render_template('register.html')


@login_required
def logout():
    response = make_response(render_template('login.html'))
    session.pop('username', None)
    response.set_cookie("username", '', expires=0)
    return response
