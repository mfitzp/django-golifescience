from tagmeta.models import TagMeta
from methods.models import Method

def batch_update_tag_trees():
    tags_with_parents = TagMeta.objects.exclude(parent=None)

    for tagm in tags_with_parents:

        parent_tag = tagm.parent.tag            

        print "Tag: %s; parent %s" % (tagm, parent_tag)
        # Get all objects tagged with this tag
        for tagi in tagm.tag.taggit_taggeditem_items.all():
            new_tagi = tagi
            new_tagi.id = None # Create new model
            new_tagi.tag = parent_tag
            try:
                new_tagi.save() # Duplicates skip
            except:
                pass
