from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    css_file = request.files.get('css_file')
    html_file = request.files.get('html_file')

    if css_file and html_file:
        css_file.save('static/uploads/style.css')
        html_file.save('static/uploads/index.html')

        # İşlemleri burada yapabilirsiniz

        return render_template('result.html')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
