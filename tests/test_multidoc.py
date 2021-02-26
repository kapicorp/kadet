#!/usr/bin/env python3

# Copyright 2021 The Kadet Authors
# SPDX-FileCopyrightText: 2021 The Kadet Authors <kapitan-admins@googlegroups.com>
#
# SPDX-License-Identifier: Apache-2.0

"multidoc tests"

import unittest
from kadet import BaseObj


class MultiDocTest(unittest.TestCase):
    def test_yaml_multidoc(self):
        multi_yaml_bobj = BaseObj.from_yaml_multidoc("./tests/multidoc.yaml")
        yamls = [y.dump() for y in multi_yaml_bobj]
        self.assertIsInstance(yamls, list)
        self.assertEqual(
            yamls,
            [
                {"name": "doc1", "keys": {"a": "b"}, "values": [1, 2, 3]},
                {"name": "doc2", "keys": {"c": "d"}, "values": [4, 5, 6]},
            ],
        )
