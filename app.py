from api import api_blueprint
from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# API Blueprint'ini uygulamaya ekle
app.register_blueprint(api_blueprint, url_prefix='/api')

@app.route("/")
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)