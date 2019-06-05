

from flask import Flask, request, render_template, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image
import datetime
import os
import subprocess
import sys
import zipfile

UPLOAD_FOLDER = './uploads'

app = Flask(__name__, template_folder='Template')
app.config.update(
    DEBUG=True,
    SECRET_KEY='asdasdsdf asldk sdlkf',
    WTF_CSRF_ENABLE=False
)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist('file[]')

        ratio = request.form.to_dict('ratio')
        power = int(ratio['ratio'])
        fpath = []

        if files:
            for file in files:

                # filename = secure_filename(file.filename)
                filename = file.filename
                print('имя файла:', filename, flush=True)
                try:
                    file.save(os.path.join(UPLOAD_FOLDER, filename))
                    ext = filename.rsplit('.', 1)[1]
                    input_path = os.path.join(UPLOAD_FOLDER, filename)
                    output_path = os.path.join(UPLOAD_FOLDER, filename.rsplit('.', 1)[0] + '_compressed.' + ext)
                    print('Дата: ', datetime.datetime.now(), 'Входной файл: ', input_path, 'Выходной файл: ', output_path, flush=True)

                    if ext == 'pdf':
                        compress_pdf(input_path, output_path, power)  # compress PDF
                        os.remove(input_path)
                    elif ext == 'bmp':
                        ext = 'jpg'
                        compress_img(input_path, output_path, power)  # convert BMP to JPG
                        os.remove(input_path)
                    elif ext.lower() == 'mov' or ext.lower() == 'mp4' or ext.lower() == 'mpg' or ext.lower() == 'mkv':
                        output_path = os.path.join(UPLOAD_FOLDER,
                                                             filename.rsplit('.', 1)[0] + '_compressed.' + 'mp4')
                        compress_video(input_path, output_path, power)  # compress video
                        os.remove(input_path)
                    else:
                        compress_img(input_path, output_path, power)  # compress IMG
                        os.remove(input_path)
                    fpath.append(output_path)
                except Exception as t:
                    return redirect(url_for('upload_file'))
        if len(fpath) > 1:
            z = zipfile.ZipFile('uploads/compress.zip', 'w')
            try:
                for i in fpath:
                    z.write(i, i.rsplit('/', 1)[1])
            finally:
                    z.close()
            try:
                for j in fpath:
                    os.remove(j)
            except Exception as t:
                print(t)
            return send_file('uploads/compress.zip', as_attachment=True)
        else:
            return send_file(output_path, as_attachment=True)

    return render_template('home.html')


@app.route('/dowm/<string:out>', methods=['GET', 'POST'])
def senda(out):
    print(out)
    return send_file(out, as_attachment=True)

def compress_video(input_file_path, output_file_path, power):
    if power == 0:
        converter = os.system((
            "ffmpeg -y -hide_banner -loglevel panic -i '{}' -vcodec libx264 -crf 23 -preset veryfast -c:a copy '{}'").format(input_file_path, output_file_path))
    elif power == 4:
        converter = os.system((
                                  "ffmpeg -y -hide_banner -loglevel panic -i '{}' -vcodec libx264 -crf 27 -preset veryfast -c:a copy '{}'").format(
            input_file_path, output_file_path))
    elif power == 8:
        converter = os.system((
                                  "ffmpeg -y -hide_banner -loglevel panic -i '{}' -vcodec libx264 -crf 35 -preset veryfast -c:a copy '{}'").format(
            input_file_path, output_file_path))



def compress_pdf(input_file_path, output_file_path, power):
    """Function to compress PDF via Ghostscript command line interface"""
    quality = {
        0: '/ebook',
        1: '/prepress',
        2: '/printer',
        4: '/screen',
        8: '/screen'
    }

    subprocess.call(['gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                     '-dPDFSETTINGS={}'.format(quality[power]),
                     '-dNOPAUSE', '-dQUIET', '-dBATCH',
                     '-sOutputFile={}'.format(output_file_path),
                     input_file_path]
                    )


def compress_img(imput_file_path, output_file_path, power):
    if power == 0:
        ratio, quality = 0.7, 50
    elif power == 4:
        ratio, quality = 0.5, 20
    elif power == 8:
        ratio, quality = 0.3, 10

    BeforeComp = Image.open(os.path.join(imput_file_path))
    hsize = int((float(BeforeComp.size[1]) * float(ratio)))
    wsize = int((float(BeforeComp.size[0]) * float(ratio)))
    image = BeforeComp.resize((wsize, hsize), Image.ANTIALIAS)
    image.save(output_file_path, quality=quality, optimaze=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
