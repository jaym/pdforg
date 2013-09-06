import pdfOrgConf as conf
import os
import hashlib
from pymongo import MongoClient
import datetime
import pdforg_index


indexer = pdforg_index.PdfOrgIndex()
if not os.path.exists(conf.DOCUMENT_PATH):
    os.mkdir(conf.DOCUMENT_PATH)


def get_collection():
    return MongoClient()[conf.DB_NAME].documents


def get_document_metadata(doc_id):
    collection = get_collection()
    return collection.find_one({'doc_id': doc_id})


def latest_documents():
    collection = get_collection()
    documents = list(collection.find())
    return documents


def save_document(title, fileObj):
    if not len(title):
        title = fileObj.filename

    if set(fileObj.mimetype).isdisjoint(set(conf.ALLOWED_DOC_TYPES)):
        return None

    fileHash = hashlib.md5()

    fileHash.update(fileObj.read())

    fileObj.seek(0)
    doc_id = fileHash.hexdigest()
    doc_location = "%s.pdf" % (doc_id)
    collection = get_collection()
    existing = collection.find_one({"doc_id":  doc_id})

    if not existing:
        fileObj.save(doc_location)
        collection.insert({'doc_id': doc_id,
                           'filename': fileObj.filename,
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

    # This is terrible
    for doc in docs:
        documents.append(get_document_metadata(doc['doc_id']))
    return documents

