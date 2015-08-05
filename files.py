import os
import sys
import logging
sys.path.append(os.path.join(os.path.dirname(__file__), 'libs'))

import cloudstorage as gcs 

app_bucket = "ts-zapis"


def write_file(filename, data):
    name = "/"+app_bucket+"/"+filename
    write_retry_params = gcs.RetryParams(backoff_factor=1.1)
    logging.info("opening new file %s" % name)
    gcs_file = gcs.open(name,'w', content_type='text/plain',options={'x-goog-meta-foo': 'foo', 'x-goog-meta-bar': 'bar'}, retry_params=write_retry_params)
    gcs_file.write(data)
    gcs_file.close()
    logging.info("write ok")


def read_file(filename):
    name = "/"+app_bucket+"/"+filename
    logging.info("opening file for reading %s" %name)
    gcs_file = gcs.open(name)
    data = gcs_file.read()
    gcs_file.close()
    logging.info("read ok")
    return data  


