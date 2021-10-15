#!/usr/bin/env python3

# Copyright 2021 The Kadet Authors
# SPDX-FileCopyrightText: 2021 The Kadet Authors <kapitan-admins@googlegroups.com>
#
# SPDX-License-Identifier: Apache-2.0

"dict tests"

import unittest
from collections import defaultdict

from kadet import Dict


class DictTest(unittest.TestCase):
    def test_dict_convert(self):
        base = Dict()
        base.foo = {"foo": "bar"}
        self.assertIsInstance(base.foo, Dict)

        base.bar = defaultdict(str)
        self.assertNotIsInstance(base.bar, Dict)
