import fsio
import fatcopy
import mock
try:
    import unittest2 as unittest
except ImportError:
    import unittest  # and hope for the best

class FatCopyTest(unittest.TestCase):
    def setUp(self):
        self.app = fatcopy.FatCopy()
        self.app.fs = mock.Mock()

    def test_copy_single_nodir(self):
        self.app.fs.isdir.return_value = False
        self.app.fatcopy_single("a/b/c", "d/e")

        self.assertTrue(self.app.fs.copyfile.called)
        self.assertEqual(self.app.fs.copyfile.call_args, (("a/b/c", "d/e"), {}))

    def test_copy_single_dir(self):
        self.app.fs.isdir = lambda fname: fname == "d/e"
        self.app.fatcopy_single('a/b/c', 'd/e')

        self.assertTrue(self.app.fs.copyfile.called)
        self.assertEqual(self.app.fs.copyfile.call_args, (("a/b/c", "d/e/c"), {}))

    def test_copy_single_dir_fatsafe(self):
        self.app.fs.isdir = lambda fname: fname == "d/e"
        self.app.fatcopy_single('a/b/c*?:', 'd/e')

        self.assertTrue(self.app.fs.copyfile.called)
        self.assertEqual(self.app.fs.copyfile.call_args, (("a/b/c*?:", "d/e/c___"), {}))

    def fixture(self, fs):
        self.app.fs.isdir = lambda fname: fs.get(fname) != None
        self.app.fs.listdir = lambda fname: fs.get(fname)
        self.app.fs.exists = lambda fname: fname in fs

    def test_copy_single_recurse(self):
        fs = {'Foo?': ['Bar:'], 'Foo?/Bar:': ["Baz"]}
        self.fixture(fs)
        self.app.fatcopy_single('Foo?', 'New')

        self.assertTrue(self.app.fs.mkdir.call_args, (
                (("New",), {}),
                (("New/Bar_",), {})))
        self.assertTrue(self.app.fs.copyfile.call_args, ((("Foo?/Bar:/Baz", "New/Bar_/Baz"), {})))

    def test_copy_single_recurse_dir(self):
        fs = {'Foo?': ['Bar:'], 'Foo?/Bar:': ["Baz"], 'New': []}
        self.fixture(fs)
        self.app.fatcopy_single('Foo?', 'New')

        self.assertTrue(self.app.fs.mkdir.call_args, (
                (("New/Foo_",), {}),
                (("New/Foo_/Bar_",), {})))
        self.assertTrue(self.app.fs.copyfile.call_args, ((("Foo?/Bar:/Baz", "New/Foo_/Bar_/Baz"), {})))


    def test_copy_single_dir_failure(self):
        fs = {'Foo?': ['Bar:'], 'Foo?/Bar:': ["Baz"], 'New': None}
        self.fixture(fs)
        self.assertRaises(ValueError, self.app.fatcopy_single, "Foo?", "New")
