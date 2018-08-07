from flask import Flask, request
from sklearn.externals import joblib

app = Flask(__name__)

pipeline = joblib.load('hammerspam/resources/models/model.pkl')


@app.route('/')
def index():
    return 'OK'


@app.route('/classification', methods=['POST'])
def classification():
    return pipeline.predict([request.data])[0]


if __name__ == '__main__':
    app.run()
