from zope.interface import implements
from zope.component import adapts
from Acquisition import aq_base
from plone.folder.interfaces import IOrderableFolder

from .interfaces import IOrderingKey


class TitleOrderingKey(object):
    """Generate a sort key from the title"""
    implements(IOrderingKey)
    adapts(IOrderableFolder)

    def __init__(self, context):
        self.context = context

    def get_key(self, obj):
        # Try Title Accessor
        if hasattr(aq_base(obj), 'Title'):
            title = obj.Title
            if callable(title):
                title = title()
        else:
            # Try title attribute
            title = getattr(aq_base(obj), 'title', None)

        if title is None:
            # Give up
            title = u''

        if not isinstance(title, unicode):
            # All keys must be unicode
            title = str(title).decode('utf-8')

        # Append id to title to ensure uniqueness of sort keys
        return title.lower() + u'-' + unicode(obj.getId())
