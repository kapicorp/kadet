#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 The Kadet Authors <kapitan-admins@googlegroups.com>
#
# SPDX-License-Identifier: Apache-2.0

"""Property-based tests for kadet serialization round-trips."""

import unittest

import yaml
from hypothesis import given
from hypothesis import strategies as st

from kadet import BaseObj

# JSON/YAML-compatible scalars. nan/inf excluded: they are not valid JSON and
# nan != nan would break equality assertions.
_scalars = st.none() | st.booleans() | st.integers() | st.floats(allow_nan=False, allow_infinity=False) | st.text()

# Recursive JSON-like values with string keys (the only key type YAML/JSON
# round-trips losslessly through kadet's dict-backed root).
_json_values = st.recursive(
    _scalars,
    lambda children: st.lists(children) | st.dictionaries(st.text(), children),
    max_leaves=20,
)

# Top level must be a mapping: from_dict() rejects non-dicts.
_json_dicts = st.dictionaries(st.text(), _json_values, max_size=8)


class PropertyTest(unittest.TestCase):
    @given(_json_dicts)
    def test_from_dict_dump_roundtrip(self, data):
        """from_dict(d).dump() reproduces d exactly."""
        self.assertEqual(BaseObj.from_dict(data).dump(), data)

    @given(_json_dicts)
    def test_yaml_roundtrip(self, data):
        """dump() survives a YAML serialize/parse cycle unchanged."""
        dumped = BaseObj.from_dict(data).dump()
        self.assertEqual(yaml.safe_load(yaml.dump(dumped)), dumped)


if __name__ == "__main__":
    unittest.main()
