from ftplib import FTP
from flask import Flask, request, render_template, redirect, send_file
from io import BytesIO

app = Flask(__name__)

# Konfigurasi FTP
ftp_host = ''
ftp_user = ''
ftp_password = ''

# Fungsi untuk mengupload file ke server FTP
def upload_file(file):
    try:
        ftp = FTP(ftp_host)
        ftp.login(user=ftp_user, passwd=ftp_password)

        # Membaca file dari objek BytesIO
        file_data = file.stream.read()

        # Mengirim file sebagai BytesIO ke server FTP
        ftp.storbinary('STOR {}'.format(file.filename), BytesIO(file_data))

        ftp.quit()

        file_list = get_file_list()
        file_list.append(file.filename)
    except Exception as e:
        # Tangani kesalahan jika terjadi
        print(f"Error during file upload: {str(e)}")

# Fungsi untuk mengunduh file dari server FTP
def download_file(file_name):
    try:
        ftp = FTP(ftp_host)
        ftp.login(user=ftp_user, passwd=ftp_password)

        # Membuka file sebagai BytesIO
        file_data = BytesIO()

        # Mengunduh file dari server FTP ke BytesIO
        ftp.retrbinary('RETR {}'.format(file_name), file_data.write)

        # Mengembalikan data file yang diunduh
        file_data.seek(0)
        return file_data
    except Exception as e:
        # Tangani kesalahan jika terjadi
        print(f"Error during file download: {str(e)}")

def get_file_list():
    try:
        ftp = FTP(ftp_host)
        ftp.login(user=ftp_user, passwd=ftp_password)

        file_list = ftp.nlst()

        ftp.quit()

        return file_list
    except Exception as e:
        # Tangani kesalahan jika terjadi
        print(f"Error during getting file list: {str(e)}")
        return []
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
                return send_file(file_data, attachment_filename=file_name, as_attachment=True)
            else:
                return render_template('index.html', error_message='File tidak ditemukan')
    
    file_list = get_file_list()
    return render_template('index.html', file_list=file_list)

@app.route('/uploaded')
def uploaded():
    return render_template('uploaded.html')

# Route ingin melihat daftar file
@app.route('/ftp')
def ftp_file_list():
    file_list = get_file_list()
    return render_template('ftp_file_list.html', file_list=file_list)

if __name__ == '__main__':
    app.run(debug=True)
