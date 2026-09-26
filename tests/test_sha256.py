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
            "b85c7da93e8790518898c280e15e3f1af5d46bf4aaa4407690f0f0a3b0316478",
        )

    def test_sha256_set_root_dict(self):
        bobj = BaseObj()
        bobj.root = {"a": "b", "c": "d"}
        self.assertEqual(
            bobj.sha256(),
            "b85c7da93e8790518898c280e15e3f1af5d46bf4aaa4407690f0f0a3b0316478",
        )

    def test_sha256_set_root_attrs(self):
        bobj = BaseObj()
        bobj.root.a = "b"
        bobj.root.c = "d"
        self.assertEqual(
            bobj.sha256(),
            "b85c7da93e8790518898c280e15e3f1af5d46bf4aaa4407690f0f0a3b0316478",
        )

    def test_sha256_set_root_list(self):
        bobj = BaseObj()
        bobj.root = [1, 2, 3, "a", "b", "c"]
        self.assertEqual(
            bobj.sha256(),
            "5394ed6504281f436d5c698d7ff8b1253f0c241d52877e52a9e513ccedf1daf5",
        )

    def test_sha256_key_order_invariant(self):
        # Same content, different insertion order -> identical digest.
        a = BaseObj()
        a.root.a = "b"
        a.root.c = "d"
        b = BaseObj()
        b.root.c = "d"
        b.root.a = "b"
        self.assertEqual(a.sha256(), b.sha256())
