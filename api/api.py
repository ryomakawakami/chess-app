import time
from flask import Flask

app = Flask(__name__)

@app.route('/time')
def get_current_Time():
    return {'time': time.time()}
