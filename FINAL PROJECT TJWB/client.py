from flask import Flask, request, render_template, redirect, send_file, make_response, session
from ftplib import FTP
from io import BytesIO

app = Flask(__name__)

# Konfigurasi FTP
ftp_host = "192.168.1.13"
ftp_user = 'alqa'
ftp_password = 'alqa'

# Set secret key for session management
app.secret_key = 'your_secret_key'


def get_ftp_connection():
    ftp = FTP(ftp_host)
    ftp.login(user=ftp_user, passwd=ftp_password)
    return ftp


# Fungsi untuk mengupload file ke server FTP0
def upload_file(file):
    try:
        with get_ftp_connection() as ftp:
            # Mengirim file langsung dari objek FileStorage
            ftp.storbinary('STOR {}'.format(file.filename), file.stream)

        file_list = get_file_list()
        file_list.append(file.filename)
    except Exception as e:
        # Tangani kesalahan jika terjadi
        print(f"Error during file upload: {str(e)}")


# Fungsi untuk mengunduh file dari server FTP
def download_file(file_name):
    try:
        with get_ftp_connection() as ftp:
            # Mengunduh file langsung ke objek BytesIO
            file_data = BytesIO()
            ftp.retrbinary('RETR {}'.format(file_name), file_data.write)

            # Mengembalikan data file yang diunduh
            file_data.seek(0)
            return file_data.getvalue()  # Mengubah BytesIO menjadi bytes
    except Exception as e:
        # Tangani kesalahan jika terjadi
        print(f"Error during file download: {str(e)}")


def get_file_list():
    try:
        with get_ftp_connection() as ftp:
            file_list = ftp.nlst()

        return file_list
    except Exception as e:
        # Tangani kesalahan jika terjadi
        print(f"Error during getting file list: {str(e)}")
        return []


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return render_template('login.html', error_message='Mohon lengkapi username dan password')
        if username == 'alqa' and password == 'alqa':
            session['username'] = username
            return redirect('/')
        else:
            return render_template('login.html', error_message='Invalid username or password')
    return render_template('login.html')



# Decorator to check if the user is logged in before accessing certain routes
@app.before_request
def require_login():
    if request.path != '/login' and 'username' not in session:
        return redirect('/login')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'upload_file' in request.files:
            file = request.files['upload_file']
            if file.filename == '':
                return render_template('index.html', error_message='Mohon pilih file yang ingin diunggah')
            upload_file(file)
            return redirect('/uploaded')
        elif 'download_file' in request.form:
            file_name = request.form['download_file']
            if file_name == '':
                return render_template('index.html', error_message='Mohon masukkan nama file yang ingin diunduh')
            file_data = download_file(file_name)
            if file_data:
                response = make_response(file_data)
                response.headers['Content-Disposition'] = f"attachment; filename={file_name}"
                return response
            else:
                return render_template('index.html', error_message='File tidak ditemukan')

    file_list = get_file_list()
    return render_template('index.html', file_list=file_list)


@app.route('/uploaded')
def uploaded():
    return render_template('uploaded.html')

@app.route('/delete-file', methods=['POST'])
def delete_file():
    file_name = request.form.get('file_name')
    if file_name:
        try:
            with get_ftp_connection() as ftp:
                ftp.delete(file_name)
        except Exception as e:
            print(f"Error during file deletion: {str(e)}")

    return redirect('/ftp')

# Route ingin melihat daftar file
@app.route('/ftp')
def ftp_file_list():
    file_list = get_file_list()
    return render_template('ftplist.html', file_list=file_list)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
