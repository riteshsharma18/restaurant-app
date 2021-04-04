import os

#code config start
BRAND_NAME = "Restaurant Managemnet System"
API_URL = "http://localhost:7000" #This is where API is running on the local server.
SECRET_KEY = "ANY_KEY_SET_BY_YOU"
UPLOAD_FOLDER = os.getcwd() + os.sep + 'static' + os.sep + 'images' + os.sep
MAX_CONTENT_PATH = 3e+6
#code config end