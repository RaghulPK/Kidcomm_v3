from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)

@app.route('/')
def hello_world():
    return render_template('speech_recog.html')

@app.route('/receiver', methods = ['POST'])
def postME():
    data = request.get_json()
    # data = jsonify(data)
    print(data)
    return "OK"

if __name__ == '__main__':
    app.run(debug=True)
