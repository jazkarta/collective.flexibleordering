import unittest2 as unittest
from Acquisition import Implicit
from zope.interface import directlyProvides
from plone.folder.interfaces import IOrderableFolder

from collective.flexibleordering.ordering import FlexibleIdOrdering
from collective.flexibleordering.ordering import FlexibleTitleOrdering
from collective.flexibleordering.subscriber import update_ordered_content_handler


class FakeObj(Implicit):

    def __init__(self, id, title):
        self.id = id
        self.title = title

    def Title(self):
        return self.title

    def getId(self):
        return self.id


class FakeFolder(Implicit):

    def __init__(self, ordering=FlexibleTitleOrdering, ids=()):
        self.ids = ids
        self._ordering = ordering

    def objectIds(self, **kw):
        return self.ids

    def _getOb(self, id_):
        return getattr(self, id_)

    def getOrdering(self):
        return self._ordering(self)


class TestOrdering(unittest.TestCase):

    def _makeOne(self, ordering=FlexibleTitleOrdering, ids=()):
        return FakeFolder(ids=ids, ordering=ordering).getOrdering()

    def test_insert(self):
        ordered = self._makeOne(FlexibleIdOrdering)
        ordered.context.c = FakeObj('c', 'Title 1')
        ordered.notifyAdded('c')
        self.assertEquals(ordered.idsInOrder(), ['c'])
        ordered.context.a = FakeObj('a', 'Title 2')
        ordered.notifyAdded('a')
        # We are ordering by id by default
        self.assertEquals(ordered.idsInOrder(), ['a', 'c'])
        self.assertEquals(ordered.getObjectPosition('c'), 1)
        self.assertEquals(ordered.getObjectPosition('a'), 0)

    def test_remove(self):
        ordered = self._makeOne(FlexibleIdOrdering)
        ordered.context.c = FakeObj('c', 'Title 1')
        ordered.notifyAdded('c')
        ordered.context.a = FakeObj('a', 'Title 2')
        ordered.notifyAdded('a')

        del ordered.context.c
        ordered.notifyRemoved('c')
        self.assertEquals(ordered.idsInOrder(), ['a'])

    def test_ordering_with_title(self):
        ordered = self._makeOne()
        ordered.context.c = FakeObj('c', 'Title 1')
        ordered.notifyAdded('c')
        ordered.context.a = FakeObj('a', 'Title 2')
        ordered.notifyAdded('a')
        # We are ordering by title now
        self.assertEquals(ordered.idsInOrder(), ['c', 'a'])
        self.assertEquals(ordered.getObjectPosition('c'), 0)
        self.assertEquals(ordered.getObjectPosition('a'), 1)
        self.assertEquals(list(ordered.order.keys()),
                          [u'title 1-c', u'title 2-a'])

    def test_title_change(self):
        ordered = self._makeOne(ids=('a', 'c'))
        ordered.context.c = FakeObj('c', 'Title 1')
        ordered.context.a = FakeObj('a', 'Title 2')
        ordered.notifyAdded('c')
        ordered.notifyAdded('a')

        ordered.context.c.title = 'Title 3'

        # Order key was not updated
        self.assertEquals(list(ordered.order.keys()),
                          [u'title 1-c', u'title 2-a'])

        # But we can still find the object
        self.assertEquals(ordered.getObjectPosition('c'), 0)

        # Force a reorder
        ordered.orderObjects()
        self.assertEquals(list(ordered.order.keys()),
                          [u'title 2-a', u'title 3-c'])
        self.assertEquals(ordered.getObjectPosition('c'), 1)

    def test_title_change_remove(self):
        ordered = self._makeOne()
        ordered.context.c = FakeObj('c', 'Title 1')
        ordered.notifyAdded('c')
        ordered.context.a = FakeObj('a', 'Title 2')
        ordered.notifyAdded('a')

        ordered.context.c.title = 'Title 3'

        # But we can still delete the object
        ordered.notifyRemoved('c')

        self.assertEquals(list(ordered.order.keys()),
                          [u'title 2-a'])

    def test_initial_order(self):
        ordered = self._makeOne()
        ordered.context.c = FakeObj('c', 'Title 1')
        ordered.context.a = FakeObj('a', 'Title 2')

        # Set a default folder ordering
        ordered.context.ids = ('a', 'c')

        # Initial access will generate the sort keys
        self.assertEquals(ordered.getObjectPosition('c'), 0)
        self.assertEquals(list(ordered.order.keys()),
                          [u'title 1-c', u'title 2-a'])

    def test_missing_raises(self):
        ordered = self._makeOne()
        ordered.context.c = FakeObj('c', 'Title 1')
        # Missing value lookup raises error
        self.assertRaises(ValueError, ordered.getObjectPosition, 'c')

    def test_reorder_hander(self):
        ordered = self._makeOne()
        ordered.context.c = FakeObj('c', 'Title 1')
        ordered.notifyAdded('c')
        ordered.context.a = FakeObj('a', 'Title 2')
        ordered.notifyAdded('a')

        ordered.context.c.title = 'Title 3'

        # Reordering only happens for contents of folders that are
        # IOrderableFolder and with an IFlexibleOrdering in place
        update_ordered_content_handler(ordered.context.c, None)
        self.assertEquals(list(ordered.order.keys()),
                          [u'title 1-c', u'title 2-a'])
        self.assertEquals(ordered.getObjectPosition('c'), 0)

        directlyProvides(ordered.context, IOrderableFolder)
        update_ordered_content_handler(ordered.context.c, None)
        # Force a reorder
        self.assertEquals(list(ordered.order.keys()),
                          [u'title 2-a', u'title 3-c'])
        self.assertEquals(ordered.getObjectPosition('c'), 1)
