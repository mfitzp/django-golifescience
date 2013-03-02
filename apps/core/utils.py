import datetime
# Django
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, F
from django.db.models import Avg, Max, Min, Count, Sum
# External
from actstream.models import Action, user_stream, model_stream

# Stop words for search: these are eliminated from searches to provide more accurate results
stopwords = {
    "a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all", 
    "almost", "alone", "along", "already", "also","although","always","am","among", "amongst", 
    "amoungst", "amount",  "an", "and", "another", "any","anyhow","anyone","anything","anyway", 
    "anywhere", "are", "around", "as",  "at", "back","be","became", "because","become","becomes", 
    "becoming", "been", "before", "beforehand", "behind", "being", "below", "beside", "besides", 
    "between", "beyond", "bill", "both", "bottom","but", "by", "call", "can", "cannot", "cant", 
    "co", "con", "could", "couldnt", "cry", "de", "describe", "detail", "do", "done", "down", 
    "due", "during", "each", "eg", "eight", "either", "eleven","else", "elsewhere", "empty", 
    "enough", "etc", "even", "ever", "every", "everyone", "everything", "everywhere", "except", 
    "few", "fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former", "formerly", 
    "forty", "found", "four", "from", "front", "full", "further", "get", "give", "go", "had", "has", 
    "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers", 
    "herself", "him", "himself", "his", "how", "however", "hundred", "ie", "if", "in", "inc", "indeed", 
    "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter", "latterly", "least", "less", 
    "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most", 
    "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither", "never", "nevertheless", 
    "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere", "of", "off", 
    "often", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours", 
    "ourselves", "out", "over", "own","part", "per", "perhaps", "please", "put", "rather", "re", "same", 
    "see", "seem", "seemed", "seeming", "seems", "serious", "several", "she", "should", "show", "side", 
    "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone", "something", "sometime", "sometimes", 
    "somewhere", "still", "such", "system", "take", "ten", "than", "that", "the", "their", "them", 
    "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon", 
    "these", "they", "thickv", "thin", "third", "this", "those", "though", "three", "through", "throughout", 
    "thru", "thus", "to", "together", "too", "top", "toward", "towards", "twelve", "twenty", "two", "un", 
    "under", "until", "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what", "whatever", 
    "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", 
    "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", 
    "will", "with", "within", "without", "would", "yet", "you", "your", "yours", "yourself", "yourselves", "the"
}



def actstream_action_equivalent(a, b):
    if a and b: # Not none either
        if a.actor == b.actor and \
           a.target == b.target and \
           a.action_object == b.action_object and \
           a.verb == b.verb:
            return True
    return False


def actstream_build(latest_stream_time = datetime.datetime(1900,1,1)):
    site = Site.objects.get_current()
    # For time being show all action objects on front page (not just followed)
    # as a few outstanding bugs, and traffic is low
    sct = ContentType.objects.get_for_model(Site)

    # Limits stream contents to either new site join for current site (fugly) OR everything else (filtered in loop below)
    stream_tmp = Action.objects.filter(public=1, timestamp__gt = latest_stream_time).filter(
            Q( Q(target_object_id = site.id) & Q(target_content_type = sct) ) |
            Q( ~Q(target_content_type = sct) )
        ).order_by('-timestamp')

    #FIXME: This is a hack, due to the lack of sites support in streams; bug submitted
    #       Also the object_filter stuff sucks.
    stream = list()
    summary = list()
    
    previous_item = None

    for item in stream_tmp:
        # Slightly horrid. Poor mister database
        if item.target and item.actor:

            if not actstream_action_equivalent(item, previous_item):
                if summary:
                    stream.append( {'is_summary':True, 'actions': summary} )
                    summary = list()
                stream.append(item)
            else:
                summary.append(item)                           

            if len(stream) == 25:
                break
        previous_item = item

    if summary:
        stream.append( {'is_summary':True, 'actions': summary} )

    if len(stream) == 0:
        return ([],0)
    else:
        return (stream, int(stream[0].timestamp.strftime("%s")) )

# Render stream into ajax list for sending
def actstream_render_ajax():
    pass

