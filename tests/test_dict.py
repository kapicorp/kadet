#!/usr/bin/env python3

# Copyright 2021 The Kadet Authors
# SPDX-FileCopyrightText: 2021 The Kadet Authors <kapitan-admins@googlegroups.com>
#
# SPDX-License-Identifier: Apache-2.0

"dict tests"

import copy
import unittest
from collections import defaultdict

from box import BoxList

from kadet import Dict


class DictTest(unittest.TestCase):
    def test_dict_convert(self):
        base = Dict()
        base.foo = {"foo": "bar"}
        self.assertIsInstance(base.foo, Dict)

        base.bar = defaultdict(str)
        self.assertNotIsInstance(base.bar, defaultdict)


class LazyDictTest(unittest.TestCase):
    def test_nested_values_convert_on_first_access(self):
        source = {"a": {"b": {"c": 1}}, "l": [{"x": 1}, [2, {"y": 3}]], "n": 4}
        d = Dict(source)
        self.assertIs(type(dict.__getitem__(d, "a")), dict, "stored raw until read")
        self.assertEqual(d.a.b.c, 1)
        self.assertIsInstance(dict.__getitem__(d, "a"), Dict, "converted in place")
        self.assertEqual(d.l[0].x, 1)
        self.assertEqual(d.l[1][1].y, 3)
        self.assertIsInstance(d["l"], BoxList)
        self.assertEqual(dict(d.items())["n"], 4)
        self.assertTrue(all(isinstance(v, (Dict, BoxList, int)) for v in d.values()))
        self.assertEqual(d.to_dict(), source)
        self.assertEqual(Dict(source).dump(), source, "dump of an unread Dict")
        self.assertIs(type(Dict(source).to_dict()["a"]), dict)

    def test_default_box_and_writes_still_work(self):
        d = Dict({"a": {}})
        d.missing.deep.key = 1
        d.a.new = [{"k": "v"}]
        self.assertEqual(d.to_dict(), {"a": {"new": [{"k": "v"}]}, "missing": {"deep": {"key": 1}}})
        self.assertEqual(d.a.new[0].k, "v")
        strict = Dict({"a": 1}, default_box=False)
        with self.assertRaises(KeyError):
            strict["nope"]

    def test_copy_and_equality(self):
        d = Dict({"a": {"b": [1, {"c": 2}]}})
        self.assertEqual(d, {"a": {"b": [1, {"c": 2}]}})
        c = copy.deepcopy(d)
        c.a.b[1].c = 3
        self.assertEqual(d.a.b[1].c, 2)
        self.assertEqual(c.a.b[1].c, 3)

    def test_rewrapping_changes_default_box_of_nested_values(self):
        strict = Dict({"a": {"b": {}}}, default_box=False)
        strict.a  # convert one level while strict
        relaxed = Dict(strict)
        self.assertEqual(relaxed.a.b.missing, {})
        self.assertIs(type(relaxed.a.b.missing), Dict)
        with self.assertRaises(KeyError):
            strict["a"]["b"]["missing"]
        holder = Dict()
        holder.child = strict.a
        self.assertEqual(holder.child.b.other, {})

    def test_merge_update_recurses_into_unread_values(self):
        d = Dict({"metadata": {"name": "x", "labels": {"a": "1"}}, "l": [1]})
        d.merge_update(Dict({"metadata": {"annotations": {"k": "v"}}, "l": [2]}), box_merge_lists="extend")
        self.assertEqual(
            d.to_dict(),
            {"metadata": {"name": "x", "labels": {"a": "1"}, "annotations": {"k": "v"}}, "l": [1, 2]},
        )
        d.update({"metadata": {"name": "y"}})
        self.assertEqual(d.metadata.name, "y")
        stored = d.setdefault("files", [])
        stored.append({"f": 1})
        self.assertEqual(d.files[0].f, 1)
