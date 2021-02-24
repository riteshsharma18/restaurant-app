#imports start
from flask import Flask
from flask import render_template, request, flash, redirect, url_for
from config import *
#imports end

app = Flask(__name__)




@app.route('/')
def index():
    data = {
        "brandName":BRAND_NAME
    }
    return render_template("index.html", data = data)

@app.route('/onboarding/')
def onboarding():
    data = {
        "brandName":BRAND_NAME
    }
    return render_template("signup.html",data = data)


# private content starts

@app.route('/dashboard/')
def dashboard():
    data = {
        "brandName":BRAND_NAME, 
     
    }
    return render_template("private/dashboard.html", data=data)

@app.route('/table-reservation/')
def table_reservation():
    data = {
        "brandName":BRAND_NAME, 

    }
    return render_template("private/table-reservation.html", data = data)

# private content ends
if __name__ == "__main__":
    app.run()