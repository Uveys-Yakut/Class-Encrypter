import re
import os
import base64
import hashlib

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
    new_file_path = file_path.replace('.css', '_hashed.css')
    with open(new_file_path, 'w') as file:
        file.write(content)
    return new_file_path
def replace_class_name(css_content, old_class_name, new_class_name):
    end_chars = ['.', ' ', ':', '::']
    
    old_class_name_clean = old_class_name.replace(' ', '')
    new_class_name_clean = new_class_name.replace(' ', '')
    
    pattern = rf'\.{re.escape(old_class_name_clean)}(?=[{re.escape("".join(end_chars))}])'
    
    replacement = f'.{new_class_name_clean}'
    updated_css = re.sub(pattern, replacement, css_content)
    
    return updated_css

def process_and_encrypt_class_names(css_content):
    class_names = extract_class_selectors(css_content)
    class_mapping = {}
    
    for class_name in class_names:
        class_name_clean = class_name.lstrip('.')
        encrypted_name, _ = hash_with_salt(class_name_clean)
        
        encrypted_class_name = '.' + encrypted_name
        class_mapping[class_name] = encrypted_class_name
    
    for original_class, encrypted_class in class_mapping.items():
        css_content = replace_class_name(css_content, original_class.lstrip('.'), encrypted_class.lstrip('.'))
    
    return css_content

css_file_path = 'styles.css'
css_content = read_css_file(css_file_path)
updated_css_content = process_and_encrypt_class_names(css_content)
new_file_path = write_to_new_file(css_file_path, updated_css_content)

print(f"Yeni dosya oluşturuldu: {new_file_path}")
