# SPDX-FileCopyrightText: 2021 The Kadet Authors <kapitan-admins@googlegroups.com>
#
# SPDX-License-Identifier: Apache-2.0

import hashlib
import json
from typing import Annotated

import yaml
from box import Box, BoxList
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field
from typeguard import check_type

ABORT_EXCEPTION_TYPE = ValueError


class Dict(Box):
    def __init__(self, *args, **kwargs):
        # See https://github.com/cdgriffith/Box/issues/210
        # Box options
        kwargs["default_box"] = kwargs.get("default_box", True)
        kwargs["default_box_attr"] = Dict
        kwargs["default_box_none_transform"] = False

        super().__init__(*args, **kwargs)

    def dump(self):
        return self.to_dict()


def _dump(obj):
    """Return obj as plain dicts and lists, resolving nested BaseObj and
    BaseModel values through their root.

    Builds new containers instead of writing converted children back into
    their parents: storing a dict into a Box converts it into a Box again, so
    an in-place walk re-boxes and then unboxes every subtree once per level
    of nesting.
    """
    if isinstance(obj, (BaseObj, BaseModel)):
        return _dump(obj.root)
    if isinstance(obj, dict):  # includes Dict
        return {k: _dump(v) for k, v in obj.items()}
    if isinstance(obj, (list, BoxList)):
        return [_dump(item) for item in obj]
    return obj


class BaseObj(object):
    """BaseObj."""

    def __init__(self, **kwargs):
        """Return a BaseObj.

        kwargs will be saved into self.kwargs values in self.root are
        returned as dict/list via self.dump()
        """
        self.root = Dict()
        self.kwargs = Dict(kwargs)
        self.new()
        self.body()

    def __str__(self):
        """__str__."""
        return str(self.dump())

    @classmethod
    def from_json(cls, file_path):
        """Return a BaseObj initialised with json content from file_path."""
        with open(file_path) as fp:
            json_obj = json.load(fp)
            return cls.from_dict(json_obj)

    @classmethod
    def from_yaml(cls, file_path):
        """Return a BaseObj initialised with yaml content from file_path."""
        with open(file_path) as fp:
            yaml_obj = yaml.safe_load(fp)
            return cls.from_dict(yaml_obj)

    @classmethod
    def from_yaml_multidoc(cls, file_path):
        """Return list generator of BaseObj initialised with file_path data."""
        with open(file_path) as fp:
            yaml_objs = yaml.safe_load_all(fp)
            for yaml_obj in yaml_objs:
                yield cls.from_dict(yaml_obj)

    @classmethod
    def from_dict(cls, dict_value):
        """Return a BaseObj initialise with dict_value."""
        bobj = cls()
        bobj.root = Dict(dict_value)
        return bobj

    def root_file(self, file_path):
        """Update self.root with YAML/JSON content in file_path.

        Raises ValueError if file_path does not end with .yaml, .yml or
        .json.
        """
        with open(file_path) as fp:
            if file_path.endswith(".yaml") or file_path.endswith(".yml"):
                yaml_obj = yaml.safe_load(fp)
                _copy = dict(self.root)
                _copy.update(yaml_obj)
                self.root = Dict(_copy)

            elif file_path.endswith(".json"):
                json_obj = json.load(fp)
                _copy = dict(self.root)
                _copy.update(json_obj)
                self.root = Dict(_copy)
            else:
                # XXX in Kapitan this is CompileError
                raise ABORT_EXCEPTION_TYPE("file_path is neither JSON or YAML: {}".format(file_path))

    def need(self, key, msg="key and value needed", istype=None):
        """Require that key is in self.kwargs.

        Error with msg if key not set. Raises TypeError if key value
        does not match type passed in istype.
        """
        err_msg = '{}: "{}": {}'.format(self.__class__.__name__, key, msg)
        if key not in self.kwargs:
            raise ABORT_EXCEPTION_TYPE(err_msg)  # XXX in Kapitan this is CompileError
        elif istype is not None:
            check_type(self.kwargs[key], istype)

    def optional(self, key, default=None, istype=None):
        """Set self.kwargs key as optional.

        Use default value if set. Raise TypeError if key value does not
        match type passed in istype.
        """
        if key in self.kwargs and istype is not None:
            check_type(self.kwargs[key], istype)

        if key not in self.kwargs:
            if default is None:
                self.kwargs[key] = default
            elif istype is not None:
                check_type(default, istype)
                self.kwargs[key] = default

    def new(self):
        """Initialise need()ed keys for a new BaseObj."""
        pass

    def new_with(self, **kwargs):
        """new_with.

        Parameters
        ----------
        kwargs :
            kwargs
        """
        self.kwargs.update(kwargs)
        super(type(self), self).new()

    def body(self):
        """Set values/logic for self.root."""
        pass

    def _dump(self, obj):
        return _dump(obj)

    def dump(self):
        """Return object dict/list."""
        return self._dump(self)

    def sha256(self):
        """Return sha256 hexdigest for self.root."""
        return hashlib.sha256(str(self.dump()).encode()).hexdigest()


class BaseModel(PydanticBaseModel):
    root: Annotated[Dict, Field(repr=False, exclude=True)] = Dict()
    model_config: Dict = {
        # https://docs.pydantic.dev/latest/migration/#changes-to-config
        "arbitrary_types_allowed": True,
        "extra": "allow",
    }

    def __init__(self, **data):
        super().__init__(**data)

        if hasattr(self, "new"):
            assert callable(self.new)
            self.new()

        if hasattr(self, "body"):
            assert callable(self.body)
            self.body()

    def __repr__(self):
        return f"<{self.__class__.__name__} at {hex(id(self))} {self.__dict__}>"

    def _dump(self, obj):
        return _dump(obj)

    def dump(self):
        """Return object dict/list."""
        return self._dump(self)
