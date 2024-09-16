import os
import chardet
from bs4 import BeautifulSoup
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify
from functions.css_class_encryptor import process_files

api_blueprint = Blueprint('api', __name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'html', 'css', 'php'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_css_files(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    css_files = [link.get('href') for link in soup.find_all('link', rel='stylesheet')]
    return css_files

def read_file_with_detected_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
    with open(file_path, 'r', encoding=encoding) as f:
        return f.read()
def find_zip_file(folder):
    for file in os.listdir(folder):
        if file.endswith('.zip'):
            return file
    return None

@api_blueprint.route('/upload', methods=['POST'])
def upload_file():
    if 'html_files' not in request.files or 'css_files' not in request.files:
        return jsonify({'error': 'No files part'}), 400

    html_files = request.files.getlist('html_files')
    css_files = request.files.getlist('css_files')

    uploaded_css_files = []

    for css_file in css_files:
        if css_file and allowed_file(css_file.filename):
            css_filename = secure_filename(css_file.filename)
            css_file.save(os.path.join(UPLOAD_FOLDER, css_filename))
            uploaded_css_files.append(css_filename)

    html_css_map = {}

    for html_file in html_files:
        if html_file and allowed_file(html_file.filename):
            html_filename = secure_filename(html_file.filename)
            html_path = os.path.join(UPLOAD_FOLDER, html_filename)
            html_file.save(html_path)

            html_content = read_file_with_detected_encoding(html_path)
            css_in_html = extract_css_files(html_content)

            matched_css_files = []
            for css_file in css_in_html:
                css_filename = os.path.basename(css_file)
                if css_filename in uploaded_css_files:
                    matched_css_files.append(css_filename)

            if matched_css_files:
                html_css_map[html_filename] = matched_css_files

    for file in os.listdir(UPLOAD_FOLDER):
        if file.endswith('.php'):
            file_path = os.path.join(UPLOAD_FOLDER, file)
            php_content = read_file_with_detected_encoding(file_path)
            css_in_php = extract_css_files(php_content)

            matched_css_files_php = []
            for css_file in css_in_php:
                css_filename = os.path.basename(css_file)
                if css_filename in uploaded_css_files:
                    matched_css_files_php.append(css_filename)

            if matched_css_files_php:
                html_css_map[file] = matched_css_files_php

    css_files_in_use = set()
    for css_files_in_html in html_css_map.values():
        css_files_in_use.update(css_files_in_html)
    
    all_html_php_files = {f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(('.html', '.php'))}
    html_php_files_in_use = set(html_css_map.keys())
    html_php_files_to_remove = all_html_php_files - html_php_files_in_use

    for file in html_php_files_to_remove:
        file_path = os.path.join(UPLOAD_FOLDER, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

    css_files_in_use = {f for f in uploaded_css_files if f in css_files_in_use}
    all_css_files = {f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.css')}
    css_files_to_remove = all_css_files - css_files_in_use

    for file in css_files_to_remove:
        file_path = os.path.join(UPLOAD_FOLDER, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

    process_files(html_css_map)

    zip_filename = find_zip_file(UPLOAD_FOLDER)
    if zip_filename is None:
        return jsonify({'error': 'Zip file not found'}), 500

    zip_file_url = f"/static/uploads/{zip_filename}"

    return jsonify({
        'html_css_map': html_css_map,
        'zip_file_url': zip_file_url
    })

