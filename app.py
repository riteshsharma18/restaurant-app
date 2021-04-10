# imports start
from flask import Flask, jsonify, session
from flask import render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from config import *
import time
import requests
import os

# imports end

app = Flask(__name__)

app.secret_key = SECRET_KEY
app.config['MAX_CONTENT_PATH'] = MAX_CONTENT_PATH
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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
    categories = requests.get(API_URL + "/category/", json={"restaurant": get_user_signed_in()})
    d = categories.json()

    products = {}
    for category in d:
        r = requests.get(API_URL + "/product/", json={"restaurant": get_user_signed_in(), "category": category["id"]})
        products[category["id"]] = r.json()


    data = {
        "brandName": BRAND_NAME,
        "categories": d,
        "products": products

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

    products = {}
    for category in d:
        r = requests.get(API_URL + "/product/", json={"restaurant": get_user_signed_in(), "category": category["id"]})
        print(r.status_code)
        products[category["id"]] = r.json()

    data = {
        "brandName": BRAND_NAME,
        "products": products,
        "categories": d
    }
    print(get_user_signed_in())
    return render_template("private/menu-management.html", data=data)


@app.route('/menu-management/add-category/', methods=["POST"])
def menu_management_add_category():
    if not check_user_signed_in():
        return redirect(url_for('index'))
    category = request.form['category']
    r = requests.post(API_URL + "/category/", json={"name": category, "restaurant": get_user_signed_in()})
    return redirect(url_for('menu_management'))


@app.route("/menu-management/delete-category/", methods=["GET"])
def menu_management_delete_category():
    if not check_user_signed_in():
        return redirect(url_for('index'))
    id = request.args.get("id")
    r = requests.delete(API_URL + "/category/", json={"category_id": id, "restaurant": get_user_signed_in()})
    return redirect(url_for('menu_management'))


@app.route("/menu-management/add-product/", methods=["POST"])
def menu_management_add_product():
    if not check_user_signed_in():
        return redirect(url_for('index'))
    f = request.files['product_image']
    image = f.filename
    category = request.form['category']
    productName = request.form['product_name']
    price = request.form['price']
    variants = request.form['variants'].split(",")
    data = {
        "image": image,
        "category": category,
        "name": productName,
        "price": price,
        "variants": variants,
        "restaurant": get_user_signed_in()
    }
    if not os.path.exists(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)
    f.save(os.path.join(UPLOAD_FOLDER, image))
    r = requests.post(API_URL + "/product/", json=data)
    if r.json()["status"] == "OK":
        return redirect(url_for('menu_management', product="added"))
    return redirect(url_for('menu_management', product="failed"))


@app.route('/menu-management/delete-product/', methods=["GET"])
def menu_management_delete_product():
    product_id = request.args.get('product', None)
    category_id = request.args.get('category', None)
    restaurant_id = request.args.get('restaurant', None)
    if product_id and category_id and restaurant_id:
        requests.delete(API_URL + "/product/",
                        json={"product": product_id, "category": category_id, "restaurant": restaurant_id})
        return redirect(url_for('menu_management', deleted='true'))

    else:
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