# imports start
from flask import Flask, jsonify, session
from flask import render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from config import *
import time
import requests
import os
import datetime as dt

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
    print(categories)
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
    if not check_user_signed_in():
        return redirect(url_for('index'))

    floors = requests.get(API_URL + "/table/", json = {'restaurant':get_user_signed_in()})
    floors = floors.json()
    for floor in floors:
       

        for table in floor['tables']:
            if table["bookedTill"] != None:
                table['bookedTill'] = int(int(table['bookedTill'])/1000)
                print(table)
            else:
                table['bookedTill']=0

    
    
    data = {
        "brandName": BRAND_NAME,
        "floors":floors,
        "currentTime":int(dt.datetime.timestamp(dt.datetime.now()))

    }
    return render_template("private/table-reservation.html", data=data)


@app.route("/table-reservation/add-floor/")
def table_reservation_add_floor():
    if not check_user_signed_in():
        return redirect(url_for('index'))
    
    r = requests.post(API_URL + '/table/', json = {'restaurant':get_user_signed_in(), 'floor_flag':1})
    if r.status_code == 200:
        return redirect(url_for('table_reservation'))

@app.route("/table-reservation/delete-floor/")
def table_reservation_delete_floor():
    if not check_user_signed_in():
        return redirect(url_for('index'))
    r = requests.delete(API_URL + '/table/', json = {'restaurant':get_user_signed_in(), 'floor':floor})
    if r.status_code == 200:
        return redirect(url_for('table_reservation'))
@app.route("/table-reservation/add-table/" , methods=["POST"])
def table_reservation_add_table():
    if not check_user_signed_in():
        return redirect(url_for('index'))
    json = request.form


    name = json.get("name","")
   
    location = json.get("location","")
    floor = json.get("floor","")
    print(floor)
    r = requests.post(API_URL + '/table/', json = {'restaurant':get_user_signed_in(), 'table':{'name':name, 'location':location }, 'floor':floor})
    print(r.json())
    if r.status_code == 200:
        return redirect(url_for('table_reservation', added=True))
    else:
        return redirect(url_for('table_reservation', added=False))

    

@app.route("/table-reservation/reserve/" , methods=["POST"])
def table_reservation_reserve():
    if not check_user_signed_in():
        return redirect(url_for('index'))
    json = request.form


    ticks = json.get("ticks","")
    floor = json.get("floor","")
    table = json.get("table","")
    print(ticks,floor,table)
    r = requests.put(API_URL + '/table/', json = {'restaurant':get_user_signed_in(), 'table':table, 'floor':floor, 'ticks':ticks})
    print(r.json())
    if r.status_code == 200:
        return redirect(url_for('table_reservation', reserved=True))
    else:
        return redirect(url_for('table_reservation', reserved=False))

    


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
    variants = [variant.strip() for variant in variants]
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





@app.route("/orders/create/" , methods=["POST"])
def orders_create():
    data = request.json #data contains all the products. 

    total = sum([float(x['price']) * float(x['qty'] ) for x in data])

    details = {'datetime':dt.datetime.now().strftime('%c'),
        'order_total':total}
    

    r = requests.post(API_URL + "/orders/", json = {"restaurant":get_user_signed_in(), "details":details, "products":data})
    print(r.status_code)
    return {"status":"OK", "message":"Order Created Successfully", "order_total":total}


@app.route("/orders/history/")
def orders_history():
    if not check_user_signed_in():
        return redirect(url_for('index'))
    

    orders = requests.get(API_URL + "/orders/" , json={"restaurant":get_user_signed_in()})
    orders = orders.json() 
    data = {
        "brandName": BRAND_NAME,
        "orders":orders
    }
    return render_template('private/order-history.html', data = data)





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