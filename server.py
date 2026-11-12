from flask import Flask, request, send_file
import subprocess, os, tempfile, zipfile

app = Flask(__name__)

@app.route('/')
def index():
    return open('index.html').read()

@app.route('/package', methods=['POST'])
def package():
    name = request.form.get('name', 'modded.apk')
    if not name.endswith('.apk'):
        name += '.apk'

    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, 'src')
        os.makedirs(src, exist_ok=True)

        if 'files' in request.files:
            z = request.files['files']
            if z.filename.endswith('.zip'):
                with zipfile.ZipFile(z) as zf:
                    zf.extractall(src)

        out = os.path.join(tmp, name)
        subprocess.run(['java', '-jar', 'apktool.jar', 'b', src, '-o', out], check=True)
        return send_file(out, as_attachment=True, download_name=name)

@app.route('/compile-so', methods=['POST'])
def compile_so():
    f = request.files['cpp']
    with tempfile.TemporaryDirectory() as tmp:
        cpp_path = os.path.join(tmp, 'mestro_menu.cpp')
        f.save(cpp_path)
        so_path = os.path.join(tmp, 'libmestro_menu.so')
        cmd = [
            'clang++', '-shared', '-fPIC',
            '-target', 'aarch64-linux-android24',
            '-o', so_path,
            cpp_path
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return send_file(so_path, as_attachment=True, download_name='libmestro_menu.so')
        except Exception as e:
            return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
