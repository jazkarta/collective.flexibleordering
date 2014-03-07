import unittest2 as unittest
from zope.component import getGlobalSiteManager
from zope.interface import Interface, directlyProvides
from plone.folder.interfaces import IOrderableFolder
from Acquisition import Implicit

from collective.flexibleordering.interfaces import IOrderingKey
from collective.flexibleordering.ordering import FlexibleTitleOrdering
from collective.flexibleordering.keys import TitleOrderingKey
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

    def __init__(self, ids=()):
        self.ids = ids

    def objectIds(self, **kw):
        return self.ids

    def _getOb(self, id_):
        return getattr(self, id_)

    def getOrdering(self):
        return FlexibleTitleOrdering(self)


class TestOrdering(unittest.TestCase):

    def _makeOne(self, ids=()):
        return FakeFolder(ids).getOrdering()

    def _setup_title_adapter(self):
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(TitleOrderingKey, (Interface,), IOrderingKey,
                            name=u'title')

    def _unsetup_title_adapter(self):
        gsm = getGlobalSiteManager()
        gsm.unregisterAdapter(TitleOrderingKey, (Interface,), IOrderingKey,
                              name=u'title')

    def test_insert(self):
        ordered = self._makeOne()
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
        ordered = self._makeOne()
        ordered.context.c = FakeObj('c', 'Title 1')
        ordered.notifyAdded('c')
        ordered.context.a = FakeObj('a', 'Title 2')
        ordered.notifyAdded('a')

        ordered.notifyRemoved('c')
        self.assertEquals(ordered.idsInOrder(), ['a'])

    def test_ordering_with_title(self):
        self._setup_title_adapter()
        try:
            ordered = self._makeOne()
            ordered.context.c = FakeObj('c', 'Title 1')
            ordered.notifyAdded('c')
            ordered.context.a = FakeObj('a', 'Title 2')
            ordered.notifyAdded('a')
            # We are ordering by id by default
            self.assertEquals(ordered.idsInOrder(), ['c', 'a'])
            self.assertEquals(ordered.getObjectPosition('c'), 0)
            self.assertEquals(ordered.getObjectPosition('a'), 1)
            self.assertEquals(list(ordered.order.keys()),
                              [u'title 1-c', u'title 2-a'])
        finally:
            self._unsetup_title_adapter()

    def test_title_change(self):
        self._setup_title_adapter()
        try:
            ordered = self._makeOne()
            ordered.context.c = FakeObj('c', 'Title 1')
            ordered.notifyAdded('c')
            ordered.context.a = FakeObj('a', 'Title 2')
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

        finally:
            self._unsetup_title_adapter()

    def test_title_change_remove(self):
        self._setup_title_adapter()
        try:
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
        finally:
            self._unsetup_title_adapter()

    def test_initial_order(self):
        self._setup_title_adapter()
        try:
            ordered = self._makeOne()
            ordered.context.c = FakeObj('c', 'Title 1')
            ordered.context.a = FakeObj('a', 'Title 2')

            # Set a default folder ordering
            ordered.context.ids = ('a', 'c')

            # Initial access will generate the sort keys
            self.assertEquals(ordered.getObjectPosition('c'), 0)
            self.assertEquals(list(ordered.order.keys()),
                              [u'title 1-c', u'title 2-a'])
        finally:
            self._unsetup_title_adapter()

    def test_missing_raises(self):
        self._setup_title_adapter()
        try:
            ordered = self._makeOne()
            ordered.context.c = FakeObj('c', 'Title 1')
            # Missing value lookup raises error
            self.assertRaises(ValueError, ordered.getObjectPosition, 'c')
        finally:
            self._unsetup_title_adapter()

    def test_reorder_hander(self):
        self._setup_title_adapter()
        try:
            ordered = self._makeOne()
            directlyProvides(ordered.context, IOrderableFolder)
            ordered.context.c = FakeObj('c', 'Title 1')
            ordered.notifyAdded('c')
            ordered.context.a = FakeObj('a', 'Title 2')
            ordered.notifyAdded('a')

            ordered.context.c.title = 'Title 3'

            # Reorder the changed item
            update_ordered_content_handler(ordered.context.c, None)

            # Force a re
            self.assertEquals(list(ordered.order.keys()),
                              [u'title 2-a', u'title 3-c'])
            self.assertEquals(ordered.getObjectPosition('c'), 1)
        finally:
            self._unsetup_title_adapter()
