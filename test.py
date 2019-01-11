from flask import make_response,Flask,json
app = Flask(__name__)

@app.route('/python')
def python():
    users=['liu','xie','a']
    return json.dumps(users,ensure_ascii=False),200,[('Content-Type','application/json;charset=UTF-8')]

if __name__ == '__main__' :
    app.run()
