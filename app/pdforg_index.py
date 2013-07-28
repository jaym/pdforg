from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser
import pdfOrgConf as conf
import os
import Queue
import threading
import commands


class PdfOrgIndex(object):
    def __init__(self, index_path=None):
        if not index_path:
            index_path = conf.INDEX_PATH

        if not os.path.exists(index_path):
            os.mkdir(index_path)
            schema = Schema(title=TEXT(stored=True), content=TEXT,
                            doc_id=ID(stored=True))
            self.ix = create_in(index_path, schema)
        else:
            self.ix = open_dir(index_path)

        self.work_queue = Queue.Queue()
        self.worker_thread = threading.Thread(target=self.indexer)
        self.worker_thread.daemon = True
        self.worker_thread.start()

    def indexer(self):
        print "Launched indexer"
        while True:
            try:
                doc_id, title, path = self.work_queue.get()
                content = unicode(commands.getoutput('pdftotext %s -' % (path)),
                                  errors='ignore')
                writer = self.ix.writer()
                writer.add_document(title=title, doc_id=doc_id,
                                    content=content)
                writer.commit()
            except:
                pass

    def index_file(self, doc_id, title, path):
        self.work_queue.put((doc_id, title, path), True)

    def search_content(self, querystr):
        with self.ix.searcher() as searcher:
            query = QueryParser("content", self.ix.schema).parse(querystr)
            results = searcher.search(query)
            r = []
            for hit in results:
                r.append({'doc_id': hit['doc_id'], 'title': hit['title']})

            return r

    def search_title(self, querystr):
        with self.ix.searcher() as searcher:
            query = QueryParser("title", self.ix.schema).parse(querystr)
            results = searcher.search(query)
            r = []
            for hit in results:
                r.append({'doc_id': hit['doc_id'], 'title': hit['title']})

            return r
