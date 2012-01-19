from mapstream2.listener.models import *
from mapstream2.listener.loader import *
from mapstream2.sherlock.search import FacebookAgent
from mapstream2.listener.greader.googlereader import *
from mapstream2.listener.greader.url import *
from mapstream2.listener.greader.items import *
from mapstream2.listener.greader.auth import *


def run():
    ds = DataSource.objects.all()[3]
    gr = GoogleReaderLoader(ds)
    print "calling load on google reader feed"
    gr.load()


