#!/usr/bin/env python3

# Copyright 2021 The Kadet Authors
# SPDX-FileCopyrightText: 2021 The Kadet Authors <kapitan-admins@googlegroups.com>
#
# SPDX-License-Identifier: Apache-2.0

"sha256 tests"

import unittest

from kadet import BaseObj


class SHA256Test(unittest.TestCase):
    def test_sha256_from_dict(self):
        bobj = BaseObj.from_dict({"a": "b", "c": "d"})
        self.assertEqual(
            bobj.sha256(),
            "9f73f79e735571488426a6f7d7b009830fb306ee33d2952a8c6d5ffe6a86f921",
        )

    def test_sha256_set_root_dict(self):
        bobj = BaseObj()
        bobj.root = {"a": "b", "c": "d"}
        self.assertEqual(
            bobj.sha256(),
            "9f73f79e735571488426a6f7d7b009830fb306ee33d2952a8c6d5ffe6a86f921",
        )

    def test_sha256_set_root_attrs(self):
        bobj = BaseObj()
        bobj.root.a = "b"
        bobj.root.c = "d"
        self.assertEqual(
            bobj.sha256(),
            "9f73f79e735571488426a6f7d7b009830fb306ee33d2952a8c6d5ffe6a86f921",
        )

    def test_sha256_set_root_list(self):
        bobj = BaseObj()
        bobj.root = [1, 2, 3, "a", "b", "c"]
        self.assertEqual(
            bobj.sha256(),
            "456a4d603ee5135d8966a00a2d49ebd94bbb9e6564c97918d3c5472dd017e2b2",
        )
