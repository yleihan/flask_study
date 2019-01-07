from . import app_2

@app_2.route('/')
def index():
    return 'hell app 2'
