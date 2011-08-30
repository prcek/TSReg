

#from __future__ import with_statement
#from google.appengine.api import files
#from google.appengine.ext import blobstore
from django.http import HttpResponse, Http404
import csv,codecs,cStringIO
import logging


class UnicodeWriter:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        orow = []
        for s in row:
            if 'encode' in dir(s):
                orow.append(s.encode("utf-8"))
            else:
                orow.append(s)
            
        self.writer.writerow(orow)
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self



def dump_to_csv(query,out):
    wr = UnicodeWriter(out,delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)        
    for obj in query:
        logging.info(obj.as_csv_row())
        wr.writerow(obj.as_csv_row())
 
#def read_csv(f, X):
#    ret = []
#    rr = UnicodeReader(f,encoding='1250', delimiter=';', quotechar='"')
#    for row in rr:
#        logging.info(row) 
#        x = X() 
#        if x.from_csv_row(row):
#            ret.append(x)
#    return ret






