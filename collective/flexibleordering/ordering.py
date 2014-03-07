from blist import sorteddict
from zope.interface import implements
from zope.component import adapts
from zope.component import queryAdapter
from Acquisition import aq_base
from plone.folder.interfaces import IOrderableFolder
from plone.memoize import instance

from .interfaces import IOrderingKey
from .interfaces import IFlexibleOrdering


class FlexibleIdOrdering(object):
    """This implementation uses an ordered dictionary for storing an
    sort-key -> id mapping"""
    implements(IFlexibleOrdering)
    adapts(IOrderableFolder)

    _order_attr = '_flexible_ordering'
    ordering_name = u'id'

    def __init__(self, context):
        self.context = context

    @property
    def order(self):
        order_attr = self._order_attr
        context = aq_base(self.context)
        # We store ordering on the context.  This could get quite
        # large, but it will be used often enough that including it on
        # the object probably makes sense.
        if not hasattr(context, self._order_attr):
            setattr(context, order_attr, sorteddict())
            # Force initial ordering
            self.orderObjects()
        return getattr(context, order_attr)

    def notifyAdded(self, id):
        assert not id in self.order
        context = aq_base(self.context)
        obj = context._getOb(id)
        key = self.key_func(obj)
        self.order[key] = id
        self.context._p_changed = True

    def notifyRemoved(self, id):
        """ see interfaces.py """
        context = aq_base(self.context)
        obj = context._getOb(id)
        key = self.key_func(obj)
        try:
            del self.order[key]
            self.context._p_changed = True      # the order was changed
            return
        except (KeyError, ValueError):
            # The key may no longer be correct, try to fetch by id
            key = self._key_for_id(id)
            if key is not None:
                del self.order[key]
                self.context._p_changed = True      # the order was changed

    def idsInOrder(self):
        return list(self.order.viewvalues())

    def getObjectPosition(self, id):
        context = aq_base(self.context)
        obj = context._getOb(id)
        key = self.key_func(obj)
        keys = self.order.viewkeys()
        try:
            return keys.index(key)
        except (KeyError, ValueError):
            # The sort key has changed, we need to use a less efficient method,
            # The modified handler should prevent this from happening
            pos = self._pos_for_id(id)
            if pos is not None:
                return pos

        raise ValueError('No object with id "%s" exists.' % id)

    def orderObjects(self):
        """Implement initial ordering"""
        key_func = self.key_func
        context = aq_base(self.context)
        order = self.order
        changed = False
        if len(order) != 0:
            items = tuple(order.items())
        else:
            # Initial ordering of unordered items
            items = [(None, id_) for id_ in context.objectIds(ordered=False)]
        for key, id_ in items:
            obj = getattr(context, id_)
            new_key = key_func(obj)
            if new_key != key:
                order[new_key] = id_
                if key is not None:
                    del order[key]
                if not changed:
                    changed = True
        self.context._p_changed = changed      # the order was changed
        return -1

    @property
    @instance.memoize
    def key_func(self):
        ordering = queryAdapter(self.context, IOrderingKey,
                                name=self.ordering_name)
        if ordering is not None:
            return ordering.get_key

        # Fall back to using the id for ordering
        return lambda o: unicode(o.getId())

    def _pos_for_id(self, id_):
        order = self.order
        ids = order.viewvalues()
        try:
            return ids.index(id_)
        except (KeyError, ValueError):  # Looks like it's not here
            return

    def _key_for_id(self, id_):
        index = self._pos_for_id(id_)
        if index is not None:
            keys = self.order.viewkeys()
            return keys[index]


class FlexibleTitleOrdering(FlexibleIdOrdering):
    # We don't actually need to implement the IOrderingKey adapter
    # since id sorting is the fallback behavior.
    ordering_name = u'title'
