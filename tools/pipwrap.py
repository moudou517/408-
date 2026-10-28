"""Run pip with a patched os.mkdir so tempfile.mkdtemp() dirs stay writable.

The sandbox maps POSIX mode 0o700 onto an ACL that denies writes, which breaks
pip's unpack/install temp directories.
"""

import os
import sys

_orig_mkdir = os.mkdir


def _mkdir(path, mode=0o777, *a, **kw):
    return _orig_mkdir(path, 0o777, *a, **kw)


os.mkdir = _mkdir

import tempfile  # noqa: E402

_orig_mkdtemp = tempfile.mkdtemp


def _mkdtemp(suffix=None, prefix=None, dir=None):
    return _orig_mkdtemp(suffix=suffix, prefix=prefix, dir=dir)


tempfile.mkdtemp = _mkdtemp

if __name__ == "__main__":
    from pip._internal.cli.main import main as pip_main

    sys.exit(pip_main(sys.argv[1:]))
