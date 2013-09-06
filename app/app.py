from flask import Flask, render_template, request, redirect, abort, url_for
from flask import send_file
import pdforg
import os.path
import mimetypes
import shutil
import pdfOrgConf as conf
import glob
app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
    documents = pdforg.latest_documents()
    return render_template('doc_view.jinja2.html',
                           documents=documents,
                           page_home="active"
                           )

def data_path(path):
    return os.path.join(conf.DOCUMENT_PATH, path)

@app.route('/document/<doc_id>')
def document(doc_id):
    metadata = pdforg.get_document_metadata(doc_id)
    if metadata:
        return send_file(data_path(metadata['location']),
                         attachment_filename=metadata['filename'],
                         as_attachment=True)
    else:
        abort(404)


def upload_error():
    abort(401)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        title = request.form['document_title']
        doc_id = pdforg.save_document(title, request.files['document_data'])
        if doc_id:
            #return redirect(url_for('document', doc_id=doc_id))
            return redirect(url_for('index'))
        else:
            upload_error()
    else:
        return render_template('upload.jinja2.html', page_upload="active")

class FilesystemFile:
    def __init__(self, path):
        self.path = path
        self.filename = os.path.basename(path)
        self.mimetype = mimetypes.guess_type("file:/"+path)
        print self.mimetype
    def save(self, target_path):
        shutil.copy(self.path, data_path(target_path))
    def read(self):
        with open(self.path, "r") as f:
            return f.read()
    def seek(self, pos):
        pass

@app.route('/scan_dir', methods=['GET', 'POST'])
def scan_dir():
    if request.method == 'POST':
        path = request.form['src_path']
        doc_ids = []
        for glob_path in glob.glob(os.path.expanduser(path)):
            for root, _, files in os.walk(glob_path):
                for name in files:
                    srcFilePath = os.path.join(root,name)
                    print srcFilePath
                    doc_ids.append(pdforg.save_document("", FilesystemFile(srcFilePath)))
        if doc_ids:
            return redirect(url_for('index'))
        else:
            upload_error()
    else:
        return render_template('upload.jinja2.html', page_upload="active")


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if not query:
        return redirect(url_for('index'))
    documents = pdforg.search_documents(query)
    return render_template('search.jinja2.html',
                           documents=documents,
                           page_home="active"
                           )

if __name__ == '__main__':
    app.run()
