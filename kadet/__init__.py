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
    """A Box with attribute access and default boxes that converts lazily.

    Nested dicts and lists are stored as given and become Dict and BoxList
    on first access, so a Dict built from a large document (a rendered helm
    chart, a whole inventory) costs nothing for the parts nobody reads.
    """

    def __init__(self, *args, **kwargs):
        # See https://github.com/cdgriffith/Box/issues/210
        # Box options
        kwargs["default_box"] = kwargs.get("default_box", True)
        kwargs["default_box_attr"] = Dict
        kwargs["default_box_none_transform"] = False

        if args and isinstance(args[0], Box):
            # Start from the other box's stored values: raw ones stay raw and
            # converted ones are re-created with this box's options below.
            args = (dict(dict.items(args[0])), *args[1:])
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        if isinstance(value, Box):
            # As Box does: a stored box takes its options from this one. Box
            # re-creates it; keep the object when its options already match,
            # so that a reference held by the caller stays the stored one.
            wanted = self._Box__box_config(extra_namespace=key)
            if any(value._box_config.get(k) != v for k, v in wanted.items()):
                value = Dict(value, **wanted)
        elif isinstance(value, (dict, list)) and not isinstance(value, BoxList):
            # Raw: kept as given and converted on first access. Box's
            # bookkeeping for attribute access of unusual keys still applies.
            if self._box_config["conversion_box"]:
                self._box_config["__safe_keys"][self._safe_attr(key)] = key
            dict.__setitem__(self, key, value)
            return
        super().__setitem__(key, value)

    def update(self, *args, **kwargs):
        # Box.update bypasses __setitem__; route through it.
        for k, v in dict(*args, **kwargs).items():
            self[k] = v

    def _converted(self, key, value):
        """`value` as stored under `key`, converted in place if still raw."""
        if isinstance(value, dict) and not isinstance(value, Box):
            value = Dict(value, **self._Box__box_config(extra_namespace=key))
        elif isinstance(value, list) and not isinstance(value, BoxList):
            value = BoxList(value, **self._Box__box_config(extra_namespace=key))
        else:
            return value
        dict.__setitem__(self, key, value)
        return value

    def __getitem__(self, item, _ignore_default=False):
        return self._converted(item, super().__getitem__(item, _ignore_default))

    def items(self, dotted=False):
        if dotted:
            return super().items(dotted=True)
        return [(key, self[key]) for key in dict.keys(self)]

    def values(self):
        return [self[key] for key in dict.keys(self)]

    def to_dict(self):
        return _plain(self)

    def dump(self):
        return self.to_dict()


def _plain(value):
    """`value` as plain dicts and lists, whether converted or still raw."""
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in dict.items(value)}
    if isinstance(value, list):
        return [_plain(v) for v in value]
    return value


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
    if isinstance(obj, dict):  # Dict too: its stored values, converted or raw
        return {k: _dump(v) for k, v in dict.items(obj)}
    if isinstance(obj, list):  # BoxList too
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
