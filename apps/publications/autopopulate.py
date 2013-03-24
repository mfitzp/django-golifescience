import os.path
import string
from datetime import datetime
import urllib, re
from xml.dom.minidom import parse, parseString
# Django
from django.core import serializers
from django.conf import settings
from django.db import models

def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc

# Wrapper for service specific (below) because may want to switch out/rearrange priority
def isbn(uri):

    # AMAZON WEB SERVICES API
    data = aws(uri)

    if not data: # if AWS failed to find a result try Google Books API
        data = googlebooks(uri)
    
    return data

def googlebooks(uri):
    # Get meta from ISBN database: isbn in self.uri
    # Alternate API available at http://isbndb.com/docs/api/ provides additional information such as page numbers, language etc.
    # however misses description fields etc. A double-request may be optimal here
    f = urllib.urlopen("http://books.google.com/books/feeds/volumes?q=isbn:" + uri)
    # Build DOM for requested data
    dom = parse(f)
    f.close()

    if dom:

        data = { 'fields': {} , 'meta': {} }

        if dom.getElementsByTagName('dc:format'):
            # Iterate over available fields and pull them into our model
            for tag,field in {'dc:title':'title','dc:description':'description','dc:creator':'author','dc:publisher':'publisher','dc:date':'published'}.items():
                if dom.getElementsByTagName(tag):
                    data['fields'][ field ] = dom.getElementsByTagName(tag)[0].childNodes[0].data

            # Date format is incorrect, fix before save
            # Google passes either YYYY, YYYY-MM, YYYY-MM-DD formats
            if 'published' in data['fields']:
                d = data['fields']['published'].split('-')
                for n in range(len(d), 3):
                    d.append('1') # 1st January
                data['fields']['published'] = '-'.join(d)

        return data

    else:
        return False

def aws(uri):
    from time import strftime
    # AWS
    rq  = "GET\n"
    rq += "ecs.amazonaws.com\n"
    rq += "/onca/xml\n"
    q = "AWSAccessKeyId=" + settings.AWS_ACCESS_KEY_ID
    q += "&Keywords=" + uri
    q += "&Operation=ItemSearch&SearchIndex=Books&Service=AWSECommerceService"
    q += "&Timestamp=%s" % urllib.quote( strftime('%Y-%m-%dT%H:%M:%S.000Z') )
    q += "&Version=2009-03-31"

    import hmac, hashlib, base64
    dig = hmac.new(settings.AWS_SECRET_ACCESS_KEY, msg=rq + q, digestmod=hashlib.sha256).digest()
    signature = urllib.quote( base64.b64encode(dig).decode() )      # py3k-mode

    f = urllib.urlopen("http://ecs.amazonaws.com/onca/xml?" + q + "&Signature=" + signature )
    dom = parse(f)
    f.close()

    if dom:

        data = { 'fields': {} , 'meta': {} }

        # Iterate over available fields and pull them into our model
        for tag,field in {'Title':'title','Author':'author','Manufacturer':'publisher'}.items():
            if dom.getElementsByTagName(tag):
                data['fields'][field] = dom.getElementsByTagName(tag)[0].childNodes[0].data

        for tag,field in {'ASIN':'asin'}.items():
            if dom.getElementsByTagName(tag):
                data['meta'][field] = dom.getElementsByTagName(tag)[0].childNodes[0].data

        return data

    else:
        return False

def pmid(uri):

    # Get non-doi-available resource via ncbi SOAP service
    f = urllib.urlopen("http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=" + uri)
    # The XML returned from this is poorly formatted for use
    xml = f.read()
    f.close()

    data = { 'fields': {} , 'meta': {}, 'tags': [] }

    if xml:
        # Pubmed is horribly inconsistent with dates the following matching anything starting with a number, following by anything
        m = re.search('Name="EPubDate" Type="Date">(\d.*?)<', xml, re.S)
        if not m:
            m = re.search('Name="PubDate" Type="Date">(\d.*?)<', xml, re.S) # try alternative

        if m:
            datestr = m.group(1).strip() # strip trailing bits
            datebits = datestr.split(' ') #split on whitespace; we may have 1->3 items
            dummybits = ['Jan','01'] # Dummy date
            datebits.extend( dummybits[ len(datebits)-1: ] )
            data['fields']['published'] = datetime.strptime( ' '.join(datebits),'%Y %b %d').date()

        m = re.search('Name="Source" Type="String">(.*?)<', xml, re.S)
        if m:
            data['fields']['publisher'] = m.group(1)

        m = re.search('Name="Title" Type="String">(.*?)<', xml, re.S)
        if m:
            data['fields']['title'] = m.group(1)

        mre = re.findall( 'Name="Author" Type="String">(.*?)<', xml, re.S)
        if mre:
            data['fields']['author'] = ', '.join( mre )

        m = re.search('Name="doi" Type="String">(.*?)<', xml, re.S)
        if m:
            data['fields']['doi'] = m.group(1)


        # This is horrible; we should use the fetch XML instead of the summary above - but it's formatted differently and missing data.
        f = urllib.urlopen("http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&rettype=abstract&retmode=xml&id=" + uri)
        # We get it out as xml; pull out the abstract and the tags
        dom = parse(f)
        f.close()


        data['fields']['abstract'] = ''
        for node in dom.getElementsByTagName('AbstractText'):
            data['fields']['abstract'] += getText(node.childNodes) + '\n'


        for node in dom.getElementsByTagName('DescriptorName'):
            data['tags'].append( getText(node.childNodes) )

        for node in dom.getElementsByTagName('QualifierName'):
            data['tags'].append( getText(node.childNodes) )

        return data
    else:
        return False


def doi(uri):
    # Use the following lookup URL to return XML describing the entity in question
    f = urllib.urlopen("http://www.crossref.org/openurl?pid=egon@spenglr.com&noredirect=true&id=" + uri)
    # Build DOM for requested data
    dom = parse(f)
    f.close()

    if dom:

        data = { 'fields': {} , 'meta': {} }

        # Iterate over available fields and pull them into our model
        for tag,field in {'article_title':'title','journal_title':'publisher','contributor':'author'}.items():
            if dom.getElementsByTagName(tag):
                data['fields'][field] = dom.getElementsByTagName(tag)[0].childNodes[0].data

        # Extract data information (only year is available, must process before assigning)
        if dom.getElementsByTagName('year'):
            data['fields']['published'] = dom.getElementsByTagName('year')[0].childNodes[0].data + '-1-1'

        # Multiple contributor/author fields so handle by transforming into comma separated text field
        if dom.getElementsByTagName('contributor'):
            authors = []
            for contributor in dom.getElementsByTagName('contributor'):
                # Hacky: It pulls in the first and surname of the contributor - but if the positions in the dom tree change it will bork
                # Can't see obvious solution using the minidom
                authors.append( contributor.childNodes[1].childNodes[0].data + ' ' + contributor.childNodes[3].childNodes[0].data )

            # Should end up with "Martin Fitzpatrick, Cael Kay-Jackson" style listing of the authors pulled down
            data['fields']['author'] = ', '.join(authors)

        # Iterate over available fields and pull them into our META
        for tag,field in {'volume':'volume','issue':'issue','first_page':'first_page','last_page':'last_page'}.items():
            if dom.getElementsByTagName(tag):
                data['meta'][field]=dom.getElementsByTagName(tag)[0].childNodes[0].data

        if 'first_page' in data['meta'] and 'last_page' in data['meta']:
            data['meta']['pages'] = int(data['meta']['last_page']) - int(data['meta']['first_page'])

        return data

    else:
        return False

def http(uri):
    
    data = { 'fields': {} , 'meta': {} }
    # Open the URL, read 10k (arbitraty) for meta off media files/etc.
    try:
        f = urllib.urlopen( uri )
        raw = f.read(10240) #10K
        f.close()
        data['fields']['mimetype'] = f.info().gettype()
    except:
        data['fields']['title'] = 'Resource not found'
    else:
        if data['fields']['mimetype'] == 'text/html':
            # Put into a single line replacing \n > " " so line-break titles work
            raw = raw.replace("\n"," ")
            # HTML in data, extract title field with regexp
            s = re.search('<title(.*?)>(?P<title>.+)</title>', raw)
            if s:
                data['fields']['title'] = s.group('title')
            else:
                data['fields']['title'] = 'Untitled'

    return data

