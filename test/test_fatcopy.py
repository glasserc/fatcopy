import fsio
import fatcopy
import mock
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # and hope for the best

class FatCopyTest(unittest.TestCase):
    def setUp(self):
        self.app = fatcopy.FatCopy("foo", "bar")

    def test_copy_single_nodir(self):
        self.app.fs = mock.Mock()
        self.app.fs.isdir.return_value = False
        self.app.fatcopy_single("a/b/c", "d/e")

        self.assertTrue(self.app.fs.copyfile.called)
        self.assertEqual(self.app.fs.copyfile.call_args, (("a/b/c", "d/e"), {}))

    def test_copy_single_dir(self):
        self.app.fs = mock.Mock()
        self.app.fs.isdir = lambda fname: fname == "d/e"
        self.app.fatcopy_single('a/b/c', 'd/e')

        self.assertTrue(self.app.fs.copyfile.called)
        self.assertEqual(self.app.fs.copyfile.call_args, (("a/b/c", "d/e/c"), {}))
