#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for the main module."""
from os import path
import os
import tempfile
import re
import unittest

from bs4 import BeautifulSoup as bs  # type: ignore

import pyphen # type: ignore
from wordhyphenator.main import chunkify, hyphenate, hyphenate_end_node

def get_testdata_dir():
    test_dir = path.dirname(path.realpath(__file__))
    return path.join(test_dir, 'testdata')


def get_golden_pairs():
    testdata_dir = get_testdata_dir()
    testdata_files = os.listdir(testdata_dir)

    matches = [re.match('in(\d+).html', f) for f in testdata_files]

    def out_name(no):
        return path.join(testdata_dir, 'out{no:s}.html'.format(no=no))

    return [(path.join(testdata_dir, m.group(0)), out_name(m.group(1)))
            for m in matches if m]


def read_file(f):
    with open(f, 'r') as fd:
        return fd.read()


def assertHtmlEqual(self, a: str, b: str, msg=None):
    self.assertEqual(
        bs(a, features='html.parser').encode(formatter='html5'),
        bs(b, features='html.parser').encode(formatter='html5'), msg)


class HyphenateTestCase(unittest.TestCase):
    def setUp(self):
        self.inouts = get_golden_pairs()

    def test_chunkify(self):
        self.assertListEqual(
            chunkify('hello-wordls&nbsp; you did '),
            ['', 'hello', '-', 'wordls', '&nbsp; ', 'you', ' ', 'did', ' '])

    def test_hyphenate_doesnt_add_spurious_whitespace(self):
        self.assertEqual(hyphenate('<q>word</q>'), '<q>word</q>')

    def test_hyphenate_hyphenates_hyphenation(self):
        assertHtmlEqual(self, hyphenate('<div>&asymp; hyphenation</div>'),
                        '<div>&asymp; hy&shy;phen&shy;ation</div>')

    def test_hyphenate(self):
        for (in_file, out_file) in self.inouts:
            assertHtmlEqual(
                self, hyphenate(read_file(in_file)), read_file(out_file),
                '{in_file:s} doesn\'t match {out_file:s}.'.format(
                    in_file=in_file, out_file=out_file))

    def test_hyphenate_a_cloze_with_2_words(self):
        self.assertEqual(
            hyphenate_end_node(pyphen.Pyphen(lang='pl'),
                      r'{{c1::Przekleństwem zasobów}}'),
            '{{c1::Prze\xadkleń\xadstwem za\xadso\xadbów}}')

    def test_dont_hyphenate_sind(self):
        self.assertEqual(
            hyphenate(r'Kinder sind dumm.'), 'Kin&shy;der sind dumm.')

    def test_dont_hyphenate_round_mathjax_but_hyphenate_the_rest(self):
        # Add hello, so that the algorithm recognizes the text as English.
        self.assertEqual(
            hyphenate(r'hello \(\ldots\) digitalization').strip(),
            r'hel&shy;lo \(\ldots\) di&shy;gi&shy;ta&shy;li&shy;za&shy;tion')

    def test_dont_hyphenate_square_mathjax_but_hyphenate_the_rest(self):
        # Add hello, so that the algorithm recognizes the text as English.
        self.assertEqual(
            hyphenate('hello \[\ldots\] digitalization').strip(),
            'hel&shy;lo \[\ldots\] di&shy;gi&shy;ta&shy;li&shy;za&shy;tion')

    def test_handle_br(self):
        self.assertEqual(hyphenate('<br>'), '<br>')
