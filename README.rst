This is just a simple hack to recursively copy directories while obeying the FAT character restrictions.

Usage
=====

::

    $ fatcopy src1 src2 src3 dest

This will copy src1, src2, and src3 into dest. If dest/src1 already exists, fatcopy will "merge" all files in src1 into dest/src1.

Tests
=====

You can run ``nosetests`` or Python's builtin test discovery stuff: ``unit2 discover -s test -t .``
