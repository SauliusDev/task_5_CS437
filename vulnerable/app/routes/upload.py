from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from app.models import FileUpload
from app.utils.auth_helpers import admin_required
from app.utils.monitoring import check_and_log_file_upload
import os
import secrets
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

upload_bp = Blueprint('upload', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'.bin', '.conf'}
MAX_FILE_SIZE = 5 * 1024 * 1024

os.makedirs(os.path.join(UPLOAD_FOLDER, 'firmware'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'configs'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'encrypted'), exist_ok=True)

AES_KEY = b'12345678901234567890123456789012'

def get_file_extension(filename):
    return os.path.splitext(filename)[1].lower()

def validate_file_content(filepath):
    if not MAGIC_AVAILABLE:
        return True
    try:
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(filepath)
        
        allowed_types = [
            'application/octet-stream',
            'text/plain',
            'application/x-executable'
        ]
        
        return file_type in allowed_types
    except:
        return True

@upload_bp.route('/upload')
@admin_required
def upload_index():
    uploads = FileUpload.get_all()
    return render_template('upload.html', uploads=uploads)

@upload_bp.route('/upload/scenario1', methods=['GET', 'POST'])
@admin_required
def upload_scenario1():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file provided', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        original_filename = file.filename
        
        upload_path = os.path.join(UPLOAD_FOLDER, 'firmware', original_filename)
        file.save(upload_path)
        
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        
        FileUpload.create(
            original_filename=original_filename,
            stored_filename=original_filename,
            file_type='firmware',
            file_size=file_size,
            upload_endpoint='/upload/scenario1',
            uploaded_by=session.get('user_id'),
            is_encrypted=False
        )
        
        flash(f'File uploaded successfully: {original_filename}', 'success')
        return redirect(url_for('upload.upload_index'))
    
    return render_template('upload.html', scenario='scenario1')

@upload_bp.route('/upload/scenario2', methods=['GET', 'POST'])
@admin_required
def upload_scenario2():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file provided', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        original_filename = file.filename
        file_ext = get_file_extension(original_filename)
        
        content_length = request.headers.get('Content-Length', type=int)
        if content_length and content_length > MAX_FILE_SIZE:
            flash(f'File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB', 'danger')
            return redirect(request.url)
        
        blacklisted_extensions = ['.exe', '.sh', '.bat', '.php']
        if file_ext in blacklisted_extensions:
            flash(f'File type not allowed: {file_ext}', 'danger')
            return redirect(request.url)
        
        stored_filename = f"{secrets.token_hex(16)}_{original_filename}"
        upload_path = os.path.join(UPLOAD_FOLDER, 'firmware', stored_filename)
        file.save(upload_path)
        
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        
        FileUpload.create(
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_type='firmware',
            file_size=file_size,
            upload_endpoint='/upload/scenario2',
            uploaded_by=session.get('user_id'),
            is_encrypted=False
        )
        
        flash(f'File uploaded successfully: {original_filename}', 'success')
        return redirect(url_for('upload.upload_index'))
    
    return render_template('upload.html', scenario='scenario2')

@upload_bp.route('/upload/scenario3', methods=['GET', 'POST'])
@admin_required
def upload_scenario3():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file provided', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        original_filename = secure_filename(file.filename)
        file_content = file.read()
        
        cipher = AES.new(AES_KEY, AES.MODE_CBC)
        encrypted_content = cipher.encrypt(pad(file_content, AES.block_size))
        
        stored_filename = f"{secrets.token_hex(16)}.enc"
        upload_path = os.path.join(UPLOAD_FOLDER, 'encrypted', stored_filename)
        
        with open(upload_path, 'wb') as f:
            f.write(cipher.iv + encrypted_content)
        
        if MAGIC_AVAILABLE:
            with open(upload_path, 'rb') as f:
                temp_content = f.read(100)
                mime = magic.Magic(mime=True)
                detected_type = mime.from_buffer(temp_content)
        
        FileUpload.create(
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_type='encrypted',
            file_size=len(file_content),
            upload_endpoint='/upload/scenario3',
            uploaded_by=session.get('user_id'),
            is_encrypted=True
        )
        
        flash(f'Encrypted file uploaded successfully: {original_filename}', 'success')
        return redirect(url_for('upload.upload_index'))
    
    return render_template('upload.html', scenario='scenario3')

@upload_bp.route('/upload/scenario3/decrypt/<int:file_id>', methods=['POST'])
@admin_required
def decrypt_file(file_id):
    from app.models import get_db_connection
    
    conn = get_db_connection()
    upload = conn.execute('SELECT * FROM file_uploads WHERE id = ?', (file_id,)).fetchone()
    conn.close()
    
    if not upload or not upload['is_encrypted']:
        flash('File not found or not encrypted', 'danger')
        return redirect(url_for('upload.upload_index'))
    
    encrypted_path = os.path.join(UPLOAD_FOLDER, 'encrypted', upload['stored_filename'])
    
    if not os.path.exists(encrypted_path):
        flash('Encrypted file not found on disk', 'danger')
        return redirect(url_for('upload.upload_index'))
    
    with open(encrypted_path, 'rb') as f:
        iv = f.read(16)
        encrypted_content = f.read()
    
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    decrypted_content = unpad(cipher.decrypt(encrypted_content), AES.block_size)
    
    decrypted_filename = f"decrypted_{upload['original_filename']}"
    decrypted_path = os.path.join(UPLOAD_FOLDER, 'firmware', decrypted_filename)
    
    with open(decrypted_path, 'wb') as f:
        f.write(decrypted_content)
    
    flash(f'File decrypted successfully: {decrypted_filename}', 'success')
    return redirect(url_for('upload.upload_index'))

@upload_bp.route('/upload/secure', methods=['GET', 'POST'])
@admin_required
def upload_secure():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file provided', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        original_filename = secure_filename(file.filename)
        file_ext = get_file_extension(original_filename)
        
        if file_ext not in ALLOWED_EXTENSIONS:
            flash(f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}', 'danger')
            return redirect(request.url)
        
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            flash(f'File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB', 'danger')
            return redirect(request.url)
        
        stored_filename = f"{secrets.token_hex(16)}{file_ext}"
        
        if file_ext == '.bin':
            upload_path = os.path.join(UPLOAD_FOLDER, 'firmware', stored_filename)
            file_type = 'firmware'
        else:
            upload_path = os.path.join(UPLOAD_FOLDER, 'configs', stored_filename)
            file_type = 'config'
        
        file.save(upload_path)
        
        if not validate_file_content(upload_path):
            os.remove(upload_path)
            flash('File content validation failed', 'danger')
            return redirect(request.url)
        
        FileUpload.create(
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_type=file_type,
            file_size=file_size,
            upload_endpoint='/upload/secure',
            uploaded_by=session.get('user_id'),
            is_encrypted=False
        )
        
        flash(f'File uploaded successfully: {original_filename}', 'success')
        return redirect(url_for('upload.upload_index'))
    
    return render_template('upload.html', scenario='secure')

@upload_bp.route('/upload/encrypted', methods=['GET', 'POST'])
@admin_required
def upload_encrypted():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file provided', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        original_filename = secure_filename(file.filename)
        file_content = file.read()
        
        file_ext = get_file_extension(original_filename)
        if file_ext not in ALLOWED_EXTENSIONS:
            flash(f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}', 'danger')
            return redirect(request.url)
        
        if len(file_content) > MAX_FILE_SIZE:
            flash(f'File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB', 'danger')
            return redirect(request.url)
        
        cipher = AES.new(AES_KEY, AES.MODE_CBC)
        encrypted_content = cipher.encrypt(pad(file_content, AES.block_size))
        
        stored_filename = f"{secrets.token_hex(16)}.enc"
        upload_path = os.path.join(UPLOAD_FOLDER, 'encrypted', stored_filename)
        
        with open(upload_path, 'wb') as f:
            f.write(cipher.iv + encrypted_content)
        
        if MAGIC_AVAILABLE:
            with open(upload_path, 'rb') as f:
                temp_content = f.read(100)
                mime = magic.Magic(mime=True)
                detected_type = mime.from_buffer(temp_content)
        
        FileUpload.create(
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_type='encrypted',
            file_size=len(file_content),
            upload_endpoint='/upload/encrypted',
            uploaded_by=session.get('user_id'),
            is_encrypted=True
        )
        
        flash(f'Encrypted file uploaded successfully: {original_filename}', 'success')
        return redirect(url_for('upload.upload_index'))
    
    return render_template('upload.html', scenario='encrypted')

