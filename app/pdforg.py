import pdfOrgConf as conf
import os
import hashlib
from pymongo import MongoClient
import datetime
import pdforg_index


indexer = pdforg_index.PdfOrgIndex()


def get_collection():
    return MongoClient()[conf.DB_NAME].documents


def get_document_metadata(doc_id):
    collection = get_collection()
    return collection.find_one({'doc_id': doc_id})


def latest_documents():
    collection = get_collection()
    documents = list(collection.find())
    return documents


def save_document(title, file):
    if not len(title):
        title = file.filename

    if file.mimetype not in conf.ALLOWED_DOC_TYPES:
        return None

    hash = hashlib.md5()

    hash.update(file.read())

    file.seek(0)
    doc_id = hash.hexdigest()
    doc_location = os.path.join(conf.DOCUMENT_PATH, "%s.pdf" % (doc_id))
    collection = get_collection()
    existing = collection.find_one({"doc_id":  doc_id})

    if not existing:
        file.save(doc_location)
        collection.insert({'doc_id': doc_id,
                           'filename': file.filename,
                           'location': doc_location,
                           'title': title,
                           'categories': [],
                           'code': [],
                           'date': datetime.datetime.now()
                           })

        indexer.index_file(doc_id, title, doc_location)

    return doc_id


def search_documents(query):
    docs = indexer.search_content(query)
    documents = []
    for doc in docs:
        documents.append(get_document_metadata(doc['doc_id']))
    return documents
