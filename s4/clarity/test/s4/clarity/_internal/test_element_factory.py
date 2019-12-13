
from unittest import TestCase
from s4.clarity._internal.factory import BatchFlags, ElementFactory


class LocalLIMS(object):
    """
    We need a super small lims class to test the batch flag functions.
    """
    def __init__(self):
        self.root_uri = "http://localhost/api/v2"
        self.factories = {}


class TestElementFactory(TestCase):

    def test_are_default_batch_tags_correct_on_factory(self):

        class TestElement(object):
            """
            Note the lack of batch flag constants
            """
            pass

        # We default to false for everything.
        test_factory = ElementFactory(LocalLIMS(), TestElement)
        self.assertFalse(test_factory.can_batch_create())
        self.assertFalse(test_factory.can_batch_get())
        self.assertFalse(test_factory.can_batch_update())
        self.assertFalse(test_factory.can_query())

    def test_are_none_batch_tags_correct_on_factory(self):

        class TestElement(object):
            BATCH_FLAGS = BatchFlags.NONE

        # We default to false for everything.
        test_factory = ElementFactory(LocalLIMS(), TestElement)
        self.assertFalse(test_factory.can_batch_create())
        self.assertFalse(test_factory.can_batch_get())
        self.assertFalse(test_factory.can_batch_update())
        self.assertFalse(test_factory.can_query())

    def test_are_batch_all_tags_read_by_factory(self):

        class TestElement(object):
            BATCH_FLAGS = BatchFlags.BATCH_ALL

        test_factory = ElementFactory(LocalLIMS(), TestElement)
        self.assertTrue(test_factory.can_batch_create())
        self.assertTrue(test_factory.can_batch_get())
        self.assertTrue(test_factory.can_batch_update())
        self.assertTrue(test_factory.can_query())

    def test_are_create_batch_tags_read_by_factory(self):

        class TestElement(object):
            BATCH_FLAGS = BatchFlags.BATCH_CREATE

        test_factory = ElementFactory(LocalLIMS(), TestElement)
        self.assertTrue(test_factory.can_batch_create())
        self.assertFalse(test_factory.can_batch_get())
        self.assertFalse(test_factory.can_batch_update())
        self.assertFalse(test_factory.can_query())

    def test_are_get_batch_tags_read_by_factory(self):

        class TestElement(object):
            BATCH_FLAGS = BatchFlags.BATCH_GET

        test_factory = ElementFactory(LocalLIMS(), TestElement)
        self.assertFalse(test_factory.can_batch_create())
        self.assertTrue(test_factory.can_batch_get())
        self.assertFalse(test_factory.can_batch_update())
        self.assertFalse(test_factory.can_query())

    def test_are_batch_update_tags_read_by_factory(self):

        class TestElement(object):
            BATCH_FLAGS = BatchFlags.BATCH_UPDATE

        test_factory = ElementFactory(LocalLIMS(), TestElement)
        self.assertFalse(test_factory.can_batch_create())
        self.assertFalse(test_factory.can_batch_get())
        self.assertTrue(test_factory.can_batch_update())
        self.assertFalse(test_factory.can_query())

    def test_are_query_tags_read_by_factory(self):

        class TestElement(object):
            BATCH_FLAGS = BatchFlags.QUERY

        test_factory = ElementFactory(LocalLIMS(), TestElement)
        self.assertFalse(test_factory.can_batch_create())
        self.assertFalse(test_factory.can_batch_get())
        self.assertFalse(test_factory.can_batch_update())
        self.assertTrue(test_factory.can_query())

    def test_name_attr_default(self):

        class TestElement(object):
            pass

        # name is the default name attribute
        test_factory = ElementFactory(LocalLIMS(), TestElement)
        self.assertEqual(test_factory.name_attribute, "name")

    def test_name_attr_set(self):
        class TestElement(object):
            NAME_ATTRIBUTE = "test_name"

        test_factory = ElementFactory(LocalLIMS(), TestElement)
        self.assertEqual(test_factory.name_attribute, "test_name")

    def test_request_path(self):
        class TestElement(object):
            REQUEST_PATH = "test/path"

        test_factory = ElementFactory(LocalLIMS(), TestElement)
        self.assertTrue(test_factory.uri.endswith("test/path"))

    def test_request_path_default(self):
        class TestElement(object):
            pass

        # Look for the pluralised element name
        test_factory = ElementFactory(LocalLIMS(), TestElement)
        self.assertTrue(test_factory.uri.endswith("testelements"))