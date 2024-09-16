import os
import re
import base64
import hashlib
import zipfile
from pathlib import Path

def hash_with_salt(input_string, salt=None, length=6):
    if salt is None:
        salt = os.urandom(16)
    
    salted_input = input_string.encode() + salt
    
    hash_object = hashlib.sha256(salted_input)
    hash_bytes = hash_object.digest()
    hash_base64 = base64.urlsafe_b64encode(hash_bytes).decode()
    short_code = ''.join(filter(lambda x: not x.isdigit(), hash_base64))
    short_code = short_code.replace('-', '')
    short_code = short_code[:length]
    
    return short_code, salt

def extract_class_selectors(css_content):
    class_pattern = re.compile(r'\.[a-zA-Z_][a-zA-Z0-9_-]*')
    matches = class_pattern.findall(css_content)
    return list(set(matches))

def read_css_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def write_to_new_file(file_path, content):
    file_stem = Path(file_path).stem
    file_suffix = Path(file_path).suffix
    new_file_path = Path(file_path).parent / (file_stem + '_hashed' + file_suffix)
    
    with open(new_file_path, 'w') as file:
        file.write(content)
    
    return new_file_path

def replace_class_name(css_content, old_class_name, new_class_name):
    pattern = rf'\.{re.escape(old_class_name.lstrip("."))}(?=[\s\.\:\:\-])'
    replacement = f'.{new_class_name}'
    updated_css = re.sub(pattern, replacement, css_content)
    return updated_css

def process_and_encrypt_class_names(css_content):
    class_names = extract_class_selectors(css_content)
    class_mapping = {}
    updated_css_content = css_content
    for class_name in class_names:
        class_name_clean = class_name.lstrip('.')
        encrypted_name, _ = hash_with_salt(class_name_clean)
        encrypted_class_name = '.' + encrypted_name
        class_mapping[class_name] = encrypted_class_name
        updated_css_content = replace_class_name(updated_css_content, class_name_clean, encrypted_name)
    return updated_css_content, class_mapping

def replace_class_names_in_html(html_content, class_mapping):
    def replace_class_in_html_classes(classes_str, class_mapping):
        classes = classes_str.split()
        new_classes = []
        for class_name in classes:
            encrypted_class = class_mapping.get(f'.{class_name}', f'.{class_name}').lstrip('.')
            new_classes.append(encrypted_class)
        return ' '.join(new_classes)

    pattern = r'class=["\']([^"\']*)["\']'
    def replacer(match):
        class_str = match.group(1)
        new_class_str = replace_class_in_html_classes(class_str, class_mapping)
        return f'class="{new_class_str}"'
    
    updated_html = re.sub(pattern, replacer, html_content)
    return updated_html

def zip_files_with_folders(grouped_files, output_zip_path):
    with zipfile.ZipFile(output_zip_path, 'w') as zip_file:
        for group_number, files in enumerate(grouped_files, 1):
            folder_name = f"hashed_{group_number}"
            for file_path in files:
                zip_file.write(file_path, arcname=f"{folder_name}/{file_path.name}")
    print(f"Files zipped to: {output_zip_path}")

def delete_files(file_paths, zip_file_path):
    for file_path in file_paths:
        file_path = Path(file_path)
        if file_path != zip_file_path and file_path.is_file():
            try:
                file_path.unlink()
                print(f"Deleted file: {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
        else:
            print(f"Skipping zip file or directory: {file_path}")

def process_files(api_response, static_dir='static/uploads'):
    project_root = Path(__file__).parent.parent
    static_path = project_root / static_dir
    grouped_files = []
    
    for file_index, (file_path, css_files) in enumerate(api_response.items(), 1):
        file_path = Path(file_path)
        class_mapping = {}
        group = []
        
        for css_file in css_files:
            css_file_path = static_path / css_file

            if css_file_path.exists():
                css_content = read_css_file(css_file_path)
                if css_content:
                    updated_css_content, css_class_mapping = process_and_encrypt_class_names(css_content)
                    new_css_file_path = write_to_new_file(css_file_path, updated_css_content)
                    group.append(new_css_file_path)
                    class_mapping.update(css_class_mapping)
        
        for ext in ['html', 'php']:
            html_php_file_path = static_path / file_path.with_suffix(f'.{ext}')
            if html_php_file_path.exists():
                html_content = read_css_file(html_php_file_path)
                updated_html_content = replace_class_names_in_html(html_content, class_mapping)
                write_to_new_file(html_php_file_path, updated_html_content)

    zip_files_with_folders(grouped_files, 'output.zip')
    delete_files([f for g in grouped_files for f in g], 'output.zip')
