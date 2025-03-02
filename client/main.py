from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit-preferences', methods=['POST'])
def submit_preferences():
    preferences = request.form.get('topics')
    response = requests.post(
        'https://your-api-endpoint.amazonaws.com/dev/generate-podcast',
        json={'preferences': preferences}
    )
    return response.json()

if __name__ == '__main__':
    app.run(debug=True)