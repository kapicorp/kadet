# Easily define and reuse complex Python objects that serialize into JSON or YAML.

```python
from kadet import BaseObj
from pprint import pprint

ships = BaseObj()
ships.root.type.container = ["panamax", "suezmax", "post-panamax"]
ships.root.type.carrier = ["conventional", "geared", "gearless"]
ships.root.type.tanker = BaseObj.from_yaml("tankers.yml")

pprint(ships)

# output
{'type': {'carrier': ['conventional',
                      'geared',
                      'gearless'],
          'container': ['panamax',
                        'suezmax',
                        'post-panamax'],
          'tanker': ['oil', 'liquified-gas', 'chemical']}}
```


# Overview

## BaseObj

BaseObj implements the basic object that serializes into JSON or YAML.
Setting keys in `self.root` means they will be serialized. Keys can be set as an hierarchy of attributes.

The `self.body()` method is reserved for setting self.root on instantiation.

The example below:

```python
class MyApp(BaseObj):
  def body(self):
    self.root.name = "myapp"
    self.root.inner.foo = "bar"
    self.root.list = [1, 2, 3]

yaml.dump(MyApp().dump())
```

serializes into:

```yaml
---
name: myapp
inner:
  foo: bar
list:
  - 1
  - 2
  - 3
```

The `self.new()` method can be used to define a basic constructor.

`self.need()` checks if a key is set and errors if it isn't (with an optional custom error message).

`kwargs` that are passed onto a new instance of BaseObj are always accessible via `self.kwargs`

In this example, MyApp needs `name` and `foo` to be passed as kwargs.

```python
class MyApp(BaseObj):
  def new(self):
    self.need("name")
    self.need("foo", msg="please provide a value for foo")

  def body(self):
    self.root.name = self.kwargs.name
    self.root.inner.foo = self.kwargs.foo
    self.root.list = [1, 2, 3]

obj = MyApp(name="myapp", foo="bar")
```

## Setting a skeleton

Defining a large body with Python can be quite hard and repetitive to read and write.

The `self.root_file()` method allows importing a YAML/JSON file to set `self.root`.

MyApp's skeleton can be set instead like this:

```yaml
#skel.yml
---
name: myapp
inner:
  foo: bar
list:
  - 1
  - 2
  - 3
```

```python
class MyApp(BaseObj):
  def new(self):
    self.need("name")
    self.need("foo", msg="please provide a value for foo")
    self.root_file("path/to/skel.yml")
```

Extending a MyApp's skeleton is possible just by implementing `self.body()`:

```python
class MyApp(BaseObj):
  def new(self):
    self.need("name")
    self.need("foo", msg="please provide a value for foo")
    self.root_file("path/to/skel.yml")

  def body(self):
    self.set_replicas()
    self.root.metadata.labels = {"app": "mylabel"}

  def set_replicas(self):
    self.root.spec.replicas = 5
```

### Inheritance

Python inheritance will work as expected:

```python

class MyOtherApp(MyApp):
  def new(self):
    super().new()  # MyApp's new()
    self.need("size")

  def body(self):
    super().body()  #  we want to extend MyApp's body
    self.root.size = self.kwargs.size
    del self.root.list  # get rid of "list"

obj = MyOtherApp(name="otherapp1", foo="bar2", size=3)
yaml.dump(obj.dump())
```
serializes to:

```yaml
---
name: otherapp1
inner:
  foo: bar2
replicas: 5
size: 3
```
