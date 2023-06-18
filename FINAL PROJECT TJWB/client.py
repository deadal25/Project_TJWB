from flask import Flask, request, render_template, redirect, send_file, make_response, session
from ftplib import FTP
from io import BytesIO

app = Flask(__name__)

# Konfigurasi FTP
ftp_host = "192.168.1.13"
ftp_user = 'ServerSavvy'
ftp_password = 'Kelompok1TJW'

# Mengatur kunci rahasia untuk manajemen sesi
app.secret_key = 'your_secret_key'

#fungsi ntuk menghasilkan objek koneksi ke server FTP.
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

#fungsi untuk mendapatkan daftar file yang ada di server FTP
def get_file_list():
    try:
        with get_ftp_connection() as ftp:
            file_list = ftp.nlst()

        return file_list
    except Exception as e:
        # Tangani kesalahan jika terjadi
        print(f"Error during getting file list: {str(e)}")
        return []

#rute menuju halaman login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return render_template('login.html', error_message='Mohon lengkapi username dan password')
        if username == 'ServerSavvy' and password == 'Kelompok1TJW':
            session['username'] = username
            return redirect('/')
        else:
            return render_template('login.html', error_message='Invalid username or password')
    return render_template('login.html')

# Decorator untuk memeriksa apakah pengguna telah melakukan login sebelum mengakses rute tertentu
@app.before_request
def require_login():
    if request.path != '/login' and 'username' not in session:
        return redirect('/login')

#rute untuk mengupload file ke server FTP
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'upload_file' in request.files:
            file = request.files['upload_file']
            if file.filename == '':
                return render_template('index.html', error_message='Mohon pilih file yang ingin diunggah')
            upload_file(file)
            return redirect('/uploaded')
        #untuk rute download
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

#rute yang digunakan untuk menampilkan halaman yang menunjukkan pesan sukses setelah pengguna berhasil mengunggah file.
@app.route('/uploaded')
def uploaded():
    return render_template('uploaded.html')

# Rute untuk mengunduh file dari server FTP
@app.route('/download-file', methods=['GET'])
def download_from_ftp():
    file_name = request.args.get('file_name')
    if file_name:
        file_data = download_file(file_name)
        if file_data:
            response = make_response(file_data)
            response.headers['Content-Disposition'] = f"attachment; filename={file_name}"
            return response
    return render_template('index.html', error_message='File tidak ditemukan')


#rute yang digunakan untuk menghapus file dari server FTP
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

# Rute ingin melihat daftar file
@app.route('/ftp')
def ftp_file_list():
    file_list = get_file_list()
    return render_template('ftplist.html', file_list=file_list)


# @app.route('/logout')
# def logout():
#     session.pop('username', None)
#     return redirect('/login')

#menjalankan aplikasi Flask ketika file ini dieksekusi langsung 
if __name__ == '__main__':
    app.run(debug=True)
