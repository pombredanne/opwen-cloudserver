from flask import Flask

app = Flask(__name__)

from opwen_cloudserver import views
