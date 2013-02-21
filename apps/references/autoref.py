import os.path
import datetime, string
import urllib, re
from xml.dom.minidom import parse, parseString
# Django
from django.core import serializers
from django.conf import settings
from django.db import models
# Methodmint


def pubmed(keywords, latest_query=None):
    # Get matching publications from Pubmed service
    # We explode the keywords append [TW] for all text-search
    # then build a string for the datetime since last update

    keywordl = keywords.split(',')
    keywordq = '[TW] '.join(keywordl) + '[TW]' # produce[TW] this[TW] string[TW]

    if latest_query == None:
        timeq = ''
    else:
        timeq = '"last %d days"' % (datetime.datetime.now() - latest_query).days

    f = urllib.urlopen("http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%s %s" % (keywordq, timeq))
    # Build DOM for requested data
    dom = parse(f)
    f.close()

    uris = []

    if dom:
        if dom.getElementsByTagName('Id'):
            for item in dom.getElementsByTagName('Id'):
                uris.append( 'pmid:%d' % int( item.childNodes[0].data ) )

            uris = uris[:25] # Limit max number of subsequent requests
                

    return uris
