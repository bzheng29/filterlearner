import os
import tempfile
import shutil
import unittest

import filters

class FilterTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.orig_dir = filters.FILTERS_DIR
        filters.FILTERS_DIR = self.tempdir

    def tearDown(self):
        shutil.rmtree(self.tempdir)
        filters.FILTERS_DIR = self.orig_dir

    def test_create_difference_filter_and_apply(self):
        orig = bytes([10, 20, 30, 40, 50, 60])
        filtered = bytes([20, 30, 40, 50, 60, 70])
        diff = filters.create_difference_filter(orig, filtered)
        self.assertEqual(diff['type'], 'difference')
        self.assertAlmostEqual(diff['dr'], 10.0)
        self.assertAlmostEqual(diff['dg'], 10.0)
        self.assertAlmostEqual(diff['db'], 10.0)
        pixels = bytearray(orig)
        filters.apply_filter(pixels, diff, 255)
        self.assertEqual(pixels, bytearray(filtered))

    def test_save_filter_sanitizes_name(self):
        filters.save_filter('../../tmp/hack', {'type': 'invert'})
        expected = os.path.join(self.tempdir, 'hack.json')
        self.assertTrue(os.path.exists(expected))

if __name__ == '__main__':
    unittest.main()
