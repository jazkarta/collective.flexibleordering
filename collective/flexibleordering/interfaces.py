from zope.interface import Interface
from plone.folder.interfaces import IOrdering


class IOrderingKey(Interface):
    """ Interface for getting object ordering keys """

    def get_key(obj):
        """ return the sort key for the object, must be unicode and
        must be unique within the folder (so it's best to include the
        id to be safe)."""


class IFlexibleOrdering(IOrdering):
    """ Marker interface for flexible ordering adapter """
    pass
