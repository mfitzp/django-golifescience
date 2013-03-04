from comments.models import MPTTComment
from comments.forms import MPTTCommentForm

def get_model():
    return MPTTComment

def get_form():
    return MPTTCommentForm
