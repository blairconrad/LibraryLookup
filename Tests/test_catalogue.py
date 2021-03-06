#!/usr/bin/env python

import catalogue
import gael.testing


class MyLibrary:
    def __init__(self, name='MyLibrary'):
        self.name = name
        self. holdings = []

    def has(self, isbn):
        self.holdings.append(isbn)

    def find_item(self, isbn):
        if isbn in self.holdings:
            return 'http://my.lib/' + isbn
        return None

    def __repr__(self):
        return self.name


class MyXisbn:
    def __init__(self):
        self.edition_map = {}

    def __setitem__(self, isbn, alternates):
        self.edition_map[isbn] = [isbn] + alternates

    def find_editions(self, isbn):
        if isbn in self.edition_map:
            return self.edition_map[isbn]
        return [isbn]


def setup_module(module):
    gael.testing.setup_memcache()


def setup_function(function):
    gael.testing.flush_memcache()


def test_find_item__single_library_item_there__finds_item():
    x = MyXisbn()
    library = MyLibrary()
    library.has('1234516591')

    c = catalogue.Catalogue(x)

    found_items = c.find_item('1234516591', [library])

    assert catalogue.FindResult(
        library, 'http://my.lib/1234516591') in found_items


def test_find_item__single_library_item_not_there__does_not_find_item():
    x = MyXisbn()
    library = MyLibrary()
    library.has('1234516591')

    c = catalogue.Catalogue(x)

    found_items = c.find_item('3234514591', [library])

    assert found_items == []


def test_find_item__single_library_other_edition_there__finds_item():
    x = MyXisbn()
    x['1234516591'] = ['1234516592']

    library = MyLibrary()
    library.has('1234516592')

    c = catalogue.Catalogue(x)

    found_items = c.find_item('1234516591', [library])

    assert catalogue.FindResult(
        library, 'http://my.lib/1234516592') in found_items


def test_find_item__single_library_two_editions_there__finds_original():
    x = MyXisbn()
    x['1234516591'] = ['1234516592']

    library = MyLibrary()
    library.has('1234516591')
    library.has('1234516592')

    c = catalogue.Catalogue(x)

    found_items = c.find_item('1234516592', [library])

    assert [catalogue.FindResult(
        library, 'http://my.lib/1234516592')] == found_items


def test_find_item__two_libraries_item_in_both__finds_both():
    x = MyXisbn()

    l1 = MyLibrary('MyLibrary1')
    l1.has('1234516591')

    l2 = MyLibrary('MyLibrary2')
    l2.has('1234516591')

    c = catalogue.Catalogue(x)

    found_items = c.find_item('1234516591', [l1, l2])

    assert catalogue.FindResult(l1, 'http://my.lib/1234516591') in found_items
    assert catalogue.FindResult(l2, 'http://my.lib/1234516591') in found_items
