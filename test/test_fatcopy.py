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
        self.app.fs = mock.Mock(fsio)

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
        self.app.fs.mkdir.side_effect = lambda fname: fs.setdefault(fname, [])

    def test_copy_single_recurse(self):
        fs = {'Foo?': ['Bar:'], 'Foo?/Bar:': ["Baz"]}
        self.fixture(fs)
        self.app.fatcopy_single('Foo?', 'New')

        self.assertEqual(self.app.fs.mkdir.call_args_list, [
                (("New",), {}),
                (("New/Bar_",), {})])
        self.assertEqual(self.app.fs.copyfile.call_args_list, [(("Foo?/Bar:/Baz", "New/Bar_/Baz"), {})])

    def test_copy_single_recurse_dir(self):
        fs = {'Foo?': ['Bar:'], 'Foo?/Bar:': ["Baz"], 'New': []}
        self.fixture(fs)
        self.app.fatcopy_single('Foo?', 'New')

        self.assertEqual(self.app.fs.mkdir.call_args_list, [
                (("New/Foo_",), {}),
                (("New/Foo_/Bar_",), {})])
        self.assertEqual(self.app.fs.copyfile.call_args_list, [(("Foo?/Bar:/Baz", "New/Foo_/Bar_/Baz"), {})])

    def test_copy_single_dir_failure(self):
        fs = {'Foo?': ['Bar:'], 'Foo?/Bar:': ["Baz"], 'New': None}
        self.fixture(fs)
        self.assertRaises(ValueError, self.app.fatcopy_single, "Foo?", "New")

    def test_copy_multiple_local(self):
        fs = {'New': []}
        self.fixture(fs)
        self.app.fatcopy_list(['Foo?', 'Bar:'], 'New')

        self.assertEqual(self.app.fs.copyfile.call_args_list, [
                (('Foo?', 'New/Foo_'), {}),
                (('Bar:', 'New/Bar_'), {})])

    def test_copy_multiple_subdirs(self):
        fs = {'New': []}
        self.fixture(fs)
        self.app.fatcopy_list(['Foo?/Bar*', 'Baz/Eggs'], 'New')

        self.assertEqual(self.app.fs.copyfile.call_args_list, [
                (('Foo?/Bar*', 'New/Bar_'), {}),
                (('Baz/Eggs', 'New/Eggs'), {})])

    def test_copy_multiple_no_dir(self):
        self.fixture({})
        self.assertRaises(ValueError, self.app.fatcopy_list, ['Foo?/Bar*', 'Baz/Eggs'], 'New')

    def test_merge(self):
        fs = {'Foo?': ['Bar:'], 'Foo?/Bar:': ['Baz'], 'New': ['Foo_'], 'New/Foo_': ['Bar_'], 'New/Foo_/Bar_': ["Bleah"]}
        self.fixture(fs)
        self.app.fatcopy_single('Foo?', 'New')

        self.assertFalse(self.app.fs.mkdir.called)
        self.assertEqual(self.app.fs.copyfile.call_args_list, [
                (('Foo?/Bar:/Baz', 'New/Foo_/Bar_/Baz'), {})
                ])

    def test_copy_subdirs(self):
        fs = {'tmp': ['a', 'b'], 'tmp/a': ['foo?'], 'tmp/b': ['bar?'], 'tmp/dest': []}
        self.fixture(fs)
        self.app.fatcopy_list(['tmp/a', 'tmp/b'], 'tmp/dest')

        self.assertEqual(self.app.fs.mkdir.call_args_list, [
                (('tmp/dest/a',), {}),
                (('tmp/dest/b',), {})
                ])
        self.assertEqual(self.app.fs.copyfile.call_args_list, [
                (('tmp/a/foo?', 'tmp/dest/a/foo_'), {}),
                (('tmp/b/bar?', 'tmp/dest/b/bar_'), {})
                ])

    @unittest.skip
    def test_copy_no_overwrite(self):
        '''Test that we don't overwrite our own files'''
        fs = {'New': []}
        self.fixture(fs)
        self.app.fatcopy_list(['Foo?/Bar*', 'Baz/Bar?'], 'New')

        self.assertEqual(self.app.fs.copyfile.call_args_list, [
                (('Foo?/Bar*', 'New/Bar_'), {})
                ])
