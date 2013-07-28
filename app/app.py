from flask import Flask, render_template, request, redirect, abort, url_for
from flask import send_file
import pdforg

app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
    documents = pdforg.latest_documents()
    return render_template('doc_view.jinja2.html',
                           documents=documents,
                           page_home="active"
                           )


@app.route('/document/<doc_id>')
def document(doc_id):
    metadata = pdforg.get_document_metadata(doc_id)
    if metadata:
        return send_file(metadata['location'],
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

if __name__ == '__main__':
    app.run()
