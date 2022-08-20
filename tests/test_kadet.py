#!/usr/bin/env python3

# Copyright 2019 The Kadet Authors
# SPDX-FileCopyrightText: 2021 The Kadet Authors <kapitan-admins@googlegroups.com>
#
# SPDX-License-Identifier: Apache-2.0

"""kadet tests."""

import tempfile
import unittest
from typing import Optional

from kadet import BaseModel, BaseObj, Dict


class KadetTestModel(BaseModel):
    name: str
    size: int
    quantity: Optional[int]
    description: str = "default description"

    def body(self):
        # set root from model params
        self.root.name = self.name
        self.root.size = self.size
        self.root.description = self.description
        if self.quantity is not None:
            self.root.quantity = self.quantity

        # add extra root values
        self.root.first_key = 1
        self.root.nested.first_key = 2
        self.root["traditional_key"] = 3
        self.root.with_dict = {"A": "dict"}
        self.root.with_baseobj_init_as = BaseObj.from_dict({"init": "as"})
        bobj = BaseObj()
        bobj.root.inside = "BaseObj"
        self.root.with_baseobj = bobj
        self.root.with_another_dict = Dict({"Another": "Dict"})


class KadetTestObj(BaseObj):
    """KadetTestObj."""

    def new(self):
        """new."""
        self.need("name", "Need a name string")
        self.need("size", "Need a size int", istype=int)
        self.optional("quantity", istype=int)
        self.optional("description", default="default description", istype=str)

    def body(self):
        """body."""
        self.root.name = self.kwargs.name
        self.root.size = self.kwargs.size
        self.root.description = self.kwargs.description
        if self.kwargs.quantity is not None:
            self.root.quantity = self.kwargs.quantity
        self.root.first_key = 1
        self.root.nested.first_key = 2
        self.root["traditional_key"] = 3
        self.root.with_dict = {"A": "dict"}
        self.root.with_baseobj_init_as = BaseObj.from_dict({"init": "as"})
        bobj = BaseObj()
        bobj.root.inside = "BaseObj"
        self.root.with_baseobj = bobj
        self.root.with_another_dict = Dict({"Another": "Dict"})


class KadetTestObjWithInner(KadetTestObj):
    """KadetTestObjWithInner."""

    def body(self):
        """body."""
        super().body()

        class Inner(BaseObj):  # noqa E306
            """Inner."""

            def body(self):
                """body."""
                self.root.i_am_inside = True

        self.root.inner = Inner()


class KadetTestObjExtendedNewKwargs(KadetTestObj):
    """KadetTestObjExtendedNewKwargs."""

    def new(self):
        """new."""
        super().new_with(name="test-with-new", size=12)


class KadetTestObjExtendedNew(KadetTestObj):
    """KadetTestObjExtendedNew."""

    def new(self):
        """new."""
        self.kwargs.name = "test-with-new"
        self.kwargs.size = 12
        super().new()


class KadetTest(unittest.TestCase):
    """KadetTest."""

    def test_parse_kwargs(self):
        """test_parse_kwargs."""
        kobj = BaseObj.from_dict({"this": "that", "not_hidden": True})
        output = kobj.dump()
        desired_output = {"this": "that", "not_hidden": True}
        self.assertEqual(output, desired_output)

    def test_from_dict_assertion(self):
        """test_from_dict_assertion."""
        with self.assertRaises(ValueError):
            BaseObj.from_dict(["this", "is", "not", "a", "dict"])

    def test_dump(self):
        """test_dump."""
        kobj = KadetTestObj(name="testObj", size=5)
        output = kobj.dump()
        desired_output = {
            "name": "testObj",
            "size": 5,
            "description": "default description",
            "first_key": 1,
            "traditional_key": 3,
            "nested": {"first_key": 2},
            "with_dict": {"A": "dict"},
            "with_baseobj_init_as": {"init": "as"},
            "with_baseobj": {"inside": "BaseObj"},
            "with_another_dict": {"Another": "Dict"},
        }
        self.assertIsInstance(output, dict)
        self.assertNotIsInstance(output, Dict)
        self.assertEqual(output, desired_output)

    def test_inner(self):
        """test_inner."""
        kobj = KadetTestObjWithInner(name="testWithInnerObj", size=6)
        output = kobj.dump()
        desired_output = {
            "name": "testWithInnerObj",
            "size": 6,
            "first_key": 1,
            "description": "default description",
            "traditional_key": 3,
            "nested": {"first_key": 2},
            "with_dict": {"A": "dict"},
            "with_baseobj_init_as": {"init": "as"},
            "with_baseobj": {"inside": "BaseObj"},
            "with_another_dict": {"Another": "Dict"},
            "inner": {"i_am_inside": True},
        }
        self.assertEqual(output, desired_output)

    def test_root_list(self):
        """test_root_list."""
        kobj = BaseObj()
        kobj.root = [1, 2, 3, "a", False]
        output = kobj.dump()
        desired_output = [1, 2, 3, "a", False]
        self.assertEqual(output, desired_output)

    def test_lists(self):
        """test_lists."""
        kobj = KadetTestObj(name="testObj", size=5)
        kobj.root.with_lists = [
            Dict({"i_am_inside_a_list": True}),
            BaseObj.from_dict({"me": "too"}),
            BaseObj.from_dict(
                {
                    "list_of_objs": [
                        BaseObj.from_dict(dict(a=1, b=2)),
                        Dict(dict(c=3, d=4)),
                    ]
                }
            ),
        ]
        output = kobj.dump()
        desired_output = {
            "name": "testObj",
            "size": 5,
            "description": "default description",
            "first_key": 1,
            "traditional_key": 3,
            "nested": {"first_key": 2},
            "with_dict": {"A": "dict"},
            "with_baseobj_init_as": {"init": "as"},
            "with_baseobj": {"inside": "BaseObj"},
            "with_another_dict": {"Another": "Dict"},
            "with_lists": [
                {"i_am_inside_a_list": True},
                {"me": "too"},
                {"list_of_objs": [{"a": 1, "b": 2}, {"c": 3, "d": 4}]},
            ],
        }
        self.assertEqual(output, desired_output)

    def test_need(self):
        """test_need."""
        with self.assertRaises(ValueError):
            KadetTestObj(this_should_error=True)
        with self.assertRaises(TypeError):
            KadetTestObj(name="stone", size="huge")

    def test_new_with(self):
        """test_new_with."""
        output_new = KadetTestObjExtendedNew().dump()
        output_new_with = KadetTestObjExtendedNewKwargs().dump()
        self.assertEqual(output_new, output_new_with)

    def test_optional_typerror(self):
        """test_optional."""
        with self.assertRaises(TypeError):
            KadetTestObj(name="stone", size=2, quantity="three")

    def test_optional(self):
        """test_optional."""
        kobj = KadetTestObj(name="stone", size=2, quantity=3)
        output = kobj.dump()

        desired_output = {
            "name": "stone",
            "size": 2,
            "quantity": 3,
            "description": "default description",
            "first_key": 1,
            "traditional_key": 3,
            "nested": {"first_key": 2},
            "with_dict": {"A": "dict"},
            "with_baseobj_init_as": {"init": "as"},
            "with_baseobj": {"inside": "BaseObj"},
            "with_another_dict": {"Another": "Dict"},
        }

        self.assertEqual(output, desired_output)

    def test_skel_yaml(self):
        """test_skel_yaml."""
        yaml_file = tempfile.mktemp(suffix=".yml")
        with open(yaml_file, "w") as fp:
            fp.write("this: that\nlist: [1,2,3]\n")

        class KadetObjFromYaml(BaseObj):
            """KadetObjFromYaml."""

            def new(self):
                """new."""
                self.root_file(yaml_file)

        output = KadetObjFromYaml().dump()
        desired_output = {"this": "that", "list": [1, 2, 3]}
        self.assertEqual(output, desired_output)

    def test_skel_json(self):
        """test_skel_json."""
        json_file = tempfile.mktemp(suffix=".json")
        with open(json_file, "w") as fp:
            fp.write('{"this": "that", "list": [1,2,3]}')

        class KadetObjFromYaml(BaseObj):
            """KadetObjFromYaml."""

            def new(self):
                """new."""
                self.root_file(json_file)

        output = KadetObjFromYaml().dump()
        desired_output = {"this": "that", "list": [1, 2, 3]}
        self.assertEqual(output, desired_output)

    def test_from_json(self):
        """test_from_json."""
        json_file = tempfile.mktemp()
        with open(json_file, "w") as fp:
            fp.write('{"this": "that", "list": [1,2,3]}')

        kobj = BaseObj.from_json(json_file)
        output = kobj.dump()
        desired_output = {"this": "that", "list": [1, 2, 3]}
        self.assertEqual(output, desired_output)

    def test_from_yaml(self):
        """test_from_yaml."""
        yaml_file = tempfile.mktemp()
        with open(yaml_file, "w") as fp:
            fp.write("this: that\nlist: [1,2,3]\n")

        kobj = BaseObj.from_yaml(yaml_file)
        output = kobj.dump()
        desired_output = {"this": "that", "list": [1, 2, 3]}
        self.assertEqual(output, desired_output)

    def test_model_dump(self):
        """test_model_dump."""
        kobj = KadetTestModel(name="testObj", size=5)
        output = kobj.dump()
        desired_output = {
            "name": "testObj",
            "size": 5,
            "description": "default description",
            "first_key": 1,
            "traditional_key": 3,
            "nested": {"first_key": 2},
            "with_dict": {"A": "dict"},
            "with_baseobj_init_as": {"init": "as"},
            "with_baseobj": {"inside": "BaseObj"},
            "with_another_dict": {"Another": "Dict"},
        }
        self.assertIsInstance(output, dict)
        self.assertNotIsInstance(output, Dict)
        self.assertEqual(output, desired_output)
