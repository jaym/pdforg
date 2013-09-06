'''
Created on 2013-09-06

@author: njh
'''
import pdforg
import pdfOrgConf as conf

if __name__ == "__main__":
    import shutil
    collection = pdforg.get_collection()
    collection.remove()
    shutil.rmtree(conf.DOCUMENT_PATH)
    shutil.rmtree(conf.INDEX_PATH)
#    for x in collection.find():
#        doc_id = x['doc_id']
#        location = x['location']
#        print x
