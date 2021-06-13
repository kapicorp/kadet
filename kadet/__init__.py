# SPDX-FileCopyrightText: 2021 The Kadet Authors <kapitan-admins@googlegroups.com>
#
# SPDX-License-Identifier: Apache-2.0

import hashlib
import json
from collections import defaultdict

import yaml
from typeguard import check_type


class Dict(defaultdict):
    """Dict."""

    def __getattr__(self, name):
        """__getattr__.

        Parameters
        ----------
        name :
            name of attribute to get
        """
        return self.__getitem__(name)

    def __setattr__(self, name, value):
        """__setattr__.

        Parameters
        ----------
        name :
            name of attribute to set
        value :
            value of attribute to set
        """
        if type(value) == dict:
            value = Dict(from_dict=value)
        return self.__setitem__(name, value)

    def __repr__(self):
        """__repr__."""
        return dict.__repr__(self)

    def __init__(self, from_dict=None):
        """__init__.

        Parameters
        ----------
        from_dict :
            dictionary to load from
        """
        super().__init__(Dict)
        if from_dict:
            check_type(from_dict, from_dict, dict)
            self.update(from_dict)

    def dump(self):
        """Dump object to dict representation."""
        return dict(self)


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

    def __repr__(self):
        """__repr__."""
        return f"<{self.__class__.__name__} at {hex(id(self))} {self.dump()}>"

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
        bobj.root = Dict(from_dict=dict_value)
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
                raise ValueError(
                    "file_path is neither JSON or YAML: {}".format(file_path)
                )

    def need(self, key, msg="key and value needed", istype=None):
        """Require that key is in self.kwargs.

        Error with msg if key not set. Raises TypeError if key value
        does not match type passed in istype.
        """
        err_msg = '{}: "{}": {}'.format(self.__class__.__name__, key, msg)
        if key not in self.kwargs:
            raise ValueError(err_msg)  # XXX in Kapitan this is CompileError
        elif istype is not None:
            check_type(key, self.kwargs[key], istype)

    def optional(self, key, default=None, istype=None):
        """Set self.kwargs key as optional.

        Use default value if set. Raise TypeError if key value does not
        match type passed in istype.
        """
        if key in self.kwargs and istype is not None:
            check_type(key, self.kwargs[key], istype)

        if key not in self.kwargs:
            if default is None:
                self.kwargs[key] = default
            elif istype is not None:
                check_type(key, default, istype)
                self.kwargs[key] = default

    def new(self):
        """Initialise need()ed keys for a new BaseObj."""
        pass

    def body(self):
        """Set values/logic for self.root."""
        pass

    def _dump(self, obj):
        """Recursively update obj should it contain other BaseObj values."""
        if isinstance(obj, BaseObj):
            if isinstance(obj.root, list):
                obj.root = [self._dump(item) for item in obj.root]
                # root is just a list, return itself
                return obj.root
            else:
                for k, v in obj.root.items():
                    obj.root[k] = self._dump(v)
                if isinstance(obj.root, dict):
                    # root is just a dict, return itself
                    return obj.root
                # BaseObj needs to return dump()
                else:
                    return obj.root.dump()
        elif isinstance(obj, list):
            obj = [self._dump(item) for item in obj]
            # list has no .dump, return itself
            return obj
        elif isinstance(obj, dict):
            for k, v in obj.items():
                obj[k] = self._dump(v)
            # dict has no .dump, return itself
            return obj

        # anything else, return itself
        return obj

    def dump(self):
        """Return object dict/list."""
        return self._dump(self)

    def sha256(self):
        """Return sha256 hexdigest for self.root."""
        return hashlib.sha256(str(self.dump()).encode()).hexdigest()
