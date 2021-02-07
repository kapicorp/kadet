import inspect
import json

from addict import Dict
import yaml


class BaseObj(object):
    def __init__(self, **kwargs):
        """
        returns a BaseObj
        kwargs will be saved into self.kwargs
        values in self.root are returned as dict via self.to_dict()
        """
        self.root = Dict()
        self.kwargs = Dict(kwargs)
        self.new()
        self.body()

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return f"<{self.__class__.__name__} at {hex(id(self))} {self.to_dict()}>"

    @classmethod
    def from_json(cls, file_path):
        """
        returns a BaseObj initialised with json content
        from file_path
        """
        with open(file_path) as fp:
            json_obj = json.load(fp)
            return cls.from_dict(json_obj)

    @classmethod
    def from_yaml(cls, file_path):
        """
        returns a BaseObj initialised with yaml content
        from file_path
        """
        with open(file_path) as fp:
            yaml_obj = yaml.safe_load(fp)
            return cls.from_dict(yaml_obj)

    @classmethod
    def from_dict(cls, dict_value):
        """
        returns a BaseObj initialise with dict_value
        """
        bobj = cls()
        bobj.root = Dict(dict_value)
        return bobj

    def update_root(self, file_path):
        """
        update self.root with YAML/JSON content in file_path
        raises ValueError if file_path does not end with .yaml, .yml or .json
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
                raise ValueError("file_path is neither JSON or YAML: {}".format(file_path))

    def need(self, key, msg="key and value needed"):
        """
        requires that key is set in self.kwargs
        errors with msg if key not set
        """
        err_msg = '{}: "{}": {}'.format(self.__class__.__name__, key, msg)
        if key not in self.kwargs:
            raise ValueError(err_msg)  # XXX in Kapitan this is CompileError

    def new(self):
        """
        initialise need()ed keys for
        a new BaseObj
        """
        pass

    def body(self):
        """
        set values/logic for self.root
        """
        pass

    def _to_dict(self, obj):
        """
        recursively update obj should it contain other
        BaseObj values
        """
        if isinstance(obj, BaseObj):
            if isinstance(obj.root, list):
                obj.root = [self._to_dict(item) for item in obj.root]
                # root is just a list, return itself
                return obj.root
            else:
                for k, v in obj.root.items():
                    obj.root[k] = self._to_dict(v)
                # BaseObj needs to return to_dict()
                return obj.root.to_dict()
        elif isinstance(obj, list):
            obj = [self._to_dict(item) for item in obj]
            # list has no .to_dict, return itself
            return obj
        elif isinstance(obj, dict):
            for k, v in obj.items():
                obj[k] = self._to_dict(v)
            # dict has no .to_dict, return itself
            return obj

        # anything else, return itself
        return obj

    def to_dict(self):
        """
        returns object dict
        """
        return self._to_dict(self)

def extends(func):
    """
    extend func()
    runs super().func() and then func()
    """
    def wrapper(*args, **kwargs):
        superfunc = getattr(super(type(args[0]), args[0]), func.__name__)
        superfunc()
        func(*args, **kwargs)
    return wrapper
