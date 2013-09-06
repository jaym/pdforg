from whoosh.qparser import QueryParser
import whoosh.analysis
import whoosh.fields
import whoosh.index
import pdfOrgConf as conf
import os
import Queue
import threading
import commands
import glob


class PdfOrgIndex(object):
    def __init__(self, index_path=None):
        if not index_path:
            index_path = conf.INDEX_PATH

        self.analyzer = whoosh.analysis.RegexTokenizer() | whoosh.analysis.LowercaseFilter() | \
            whoosh.analysis.StopFilter() | whoosh.analysis.StemFilter()

        if not os.path.exists(index_path) or len(glob.glob(index_path+"/*")) == 0:
            if not os.path.exists(index_path):
                os.mkdir(index_path)
            schema = whoosh.fields.Schema(title=whoosh.fields.TEXT(stored=True, analyzer=self.analyzer),
                            content=whoosh.fields.TEXT(analyzer=self.analyzer),
                            doc_id=whoosh.fields.ID(stored=True))
            self.ix = whoosh.index.create_in(index_path, schema)
        else:
            self.ix = whoosh.index.open_dir(index_path)

        self.work_queue = Queue.Queue()
        self.worker_thread = threading.Thread(target=self.indexer)
        self.worker_thread.daemon = True
        self.worker_thread.start()

    def indexer(self):
        print "Launched indexer"
        while True:
            try:
                doc_id, title, path = self.work_queue.get()
                print "Got document %s" % (title)
                content = unicode(commands.getoutput('pdftotext %s -' % (path)),
                                  errors='ignore')
                writer = self.ix.writer()
                writer.add_document(title=unicode(title),
                                    doc_id=unicode(doc_id),
                                    content=content)
                writer.commit()
            except Exception, err:
                print err

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

if __name__ == "__main__":
    PdfOrgIndex()