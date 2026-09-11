"""Behavioural tests for pyawskit's pure file and stream helpers."""

import io
import json
import os
import tempfile
import unittest

from pyawskit import common, utils


class CopyFileObjTests(unittest.TestCase):
    def test_copies_all_bytes(self):
        payload = b"pyawskit stream copy payload" * 5000
        src = io.BytesIO(payload)
        dst = io.BytesIO()
        utils.copyfileobj(src, dst)
        self.assertEqual(dst.getvalue(), payload)

    def test_copies_across_small_buffer_boundary(self):
        payload = b"0123456789"
        src = io.BytesIO(payload)
        dst = io.BytesIO()
        utils.copyfileobj(src, dst, buffer_size=3)
        self.assertEqual(dst.getvalue(), payload)

    def test_empty_source_yields_empty_destination(self):
        dst = io.BytesIO()
        utils.copyfileobj(io.BytesIO(b""), dst)
        self.assertEqual(dst.getvalue(), b"")


class LoadJsonConfigTests(unittest.TestCase):
    def test_reads_named_config_under_home(self):
        obj = {"region": "eu-west-1", "count": 3}
        with tempfile.TemporaryDirectory() as home:
            os.mkdir(os.path.join(home, ".pyawskit"))
            with open(os.path.join(home, ".pyawskit", "settings.json"), "w", encoding="utf-8") as fh:
                json.dump(obj, fh)
            old_home = os.environ.get("HOME")
            os.environ["HOME"] = home
            try:
                self.assertEqual(common.load_json_config("settings"), obj)
            finally:
                if old_home is None:
                    del os.environ["HOME"]
                else:
                    os.environ["HOME"] = old_home


class TouchTests(unittest.TestCase):
    def test_touch_creates_empty_file(self):
        with tempfile.TemporaryDirectory() as d:
            target = os.path.join(d, "created")
            self.assertFalse(os.path.exists(target))
            common.touch(target)
            self.assertTrue(os.path.isfile(target))
            self.assertEqual(os.path.getsize(target), 0)

    def test_touch_truncates_existing_file(self):
        with tempfile.TemporaryDirectory() as d:
            target = os.path.join(d, "existing")
            with open(target, "w", encoding="utf-8") as fh:
                fh.write("previous content")
            common.touch(target)
            self.assertEqual(os.path.getsize(target), 0)

    def test_do_hush_login_creates_file_in_home(self):
        with tempfile.TemporaryDirectory() as home:
            old_home = os.environ.get("HOME")
            os.environ["HOME"] = home
            try:
                common.do_hush_login()
                self.assertTrue(os.path.isfile(os.path.join(home, ".hushlogin")))
            finally:
                if old_home is None:
                    del os.environ["HOME"]
                else:
                    os.environ["HOME"] = old_home


if __name__ == "__main__":
    unittest.main()
