# imports start
from flask import Flask, jsonify, session
from flask import render_template, request, flash, redirect, url_for
from config import *
import time
import requests

# imports end

app = Flask(__name__)

app.secret_key = SECRET_KEY


@app.route('/')
def index():
    if check_user_signed_in():
        return redirect(url_for('dashboard'))
    data = {
        "brandName": BRAND_NAME
    }
    return render_template("index.html", data=data)


@app.route('/send/', methods=["POST"])
def index_send():
    if check_user_signed_in():
        return redirect(url_for('dashboard'))
    data = {
        "email": request.form["email"],
        "password": request.form["pass"]
    }
    r = requests.get(API_URL + "/restaurant/", json=data)
    if 'email' in r.json():
        set_user_signed_in(r.json()['id'])
        return jsonify({"login": "true"})
    return jsonify({"login": "false"})


@app.route('/logout/')
def logout():
    set_user_signed_out()
    return redirect(url_for('index'))


@app.route('/onboarding/')
def onboarding():
    if check_user_signed_in():
        return redirect(url_for('dashboard'))
    data = {
        "brandName": BRAND_NAME
    }
    return render_template("signup.html", data=data)


@app.route('/onboarding/send/', methods=["POST"])
def onboarding_send():
    if check_user_signed_in():
        return redirect(url_for('dashboard'))
    data = {
        "name": request.form['rname'],
        "email": request.form['email'],
        "password": request.form["pass"]
    }

    time.sleep(4)
    r = requests.post(API_URL + "/restaurant/", json=data)
    return ""


# private content starts

@app.route('/dashboard/')
def dashboard():
    if not check_user_signed_in():
        return redirect(url_for('index'))
    data = {
        "brandName": BRAND_NAME,

    }
    return render_template("private/dashboard.html", data=data)


@app.route('/table-reservation/')
def table_reservation():
    # if not check_user_signed_in():
    #     return redirect(url_for('index'))
    data = {
        "brandName": BRAND_NAME,

    }
    return render_template("private/table-reservation.html", data=data)


@app.route('/menu-management/')
def menu_management():
    if not check_user_signed_in():
        return redirect(url_for('index'))

    categories = requests.get(API_URL + "/category/", json={"restaurant": get_user_signed_in()})
    d = categories.json()
    data = {
        "brandName": BRAND_NAME,

        "categories": d
    }
    return render_template("private/menu-management.html", data=data)


@app.route('/menu-management/add-category/', methods=["POST"])
def menu_management_add_category():
    category = request.form['category']
    r = requests.post(API_URL + "/category/", json={"name": category, "restaurant": get_user_signed_in()})
    return redirect(url_for('menu_management'))


# private content ends


# Helper Functions start

def set_user_signed_in(email):
    session['id'] = email


def set_user_signed_out():
    session.pop('id')


def check_user_signed_in():
    return 'id' in session


def get_user_signed_in():
    return session['id']


# Helper functins ends


if __name__ == "__main__":
    app.run()