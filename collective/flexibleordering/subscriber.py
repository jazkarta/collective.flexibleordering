from plone.folder.interfaces import IOrderableFolder
from Acquisition import aq_inner, aq_parent, aq_base

from .interfaces import IFlexibleOrdering


def update_ordered_content_handler(obj, event):
    parent = aq_parent(aq_inner(obj))
    if IOrderableFolder.providedBy(parent):
        ordering = parent.getOrdering()
        if IFlexibleOrdering.providedBy(ordering):
            key = ordering.key_func(obj)
            if key not in ordering.order:
                # Reinsert the object into the ordering
                obj_id = obj.getId()
                ordering.notifyRemoved(obj_id)
                ordering.notifyAdded(obj_id)
                # We need to re-reindex the order, in case we're not
                # using a Gopip index
                if hasattr(aq_base(obj), 'reindexObject'):
                    obj.reindexObject(idxs=['getObjPositionInParent'])
