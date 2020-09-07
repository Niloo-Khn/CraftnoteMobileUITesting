# standard libs
from collections.abc import Mapping, MutableMapping
from copy import copy
import re
from pprint import pformat

# third party libs

# project imports


class RecursiveDict(MutableMapping):
  """A dictionary that allows recursive and relative access to its contents."""

  def __init__(self, *args, **kwargs):
    # recursive structure
    self.root = kwargs.pop('__root', None)
    self.parent = kwargs.pop('__parent', None)
    self.key = kwargs.pop('__key', None)
    if self.parent is None:
      self.root = self

    # keys and chars used for various functionalities

    self.config = {
      'separator': '/',
      'self_key': '.',
      'parent_key': '..',
      'root_key': '...',
      'key_key': '<key>',
    }

    self.config.update(kwargs.pop('__config', {}))

    for key, default in self.config.items():
      self.config[key] = kwargs.pop('__' + key, default)

    # underlying storage
    self.store = dict()
    self.update(dict(*args, **kwargs))

  @property
  def builtin_keys(self):
    """
    Built-in keys for relative access or key access.
    """
    return [
      self.config['self_key'],
      self.config['parent_key'],
      self.config['root_key'],
      self.config['key_key'],
    ]

  @property
  def full_path(self):
    """
    Returns full path to current dictionary from root.
    """
    if self.parent is None:
      return []
    else:
      return self.parent.full_path + [self.key]

  @property
  def full_key(self):
    """
    Returns full key to current dictionary from root.
    """
    return self.path_to_key(self.full_path)

  def key_to_path(self, key):
    """
    Function that transforms key to list of keys aka path.
    By default, separates key using `separator` if it is string.
    Must return `list`, cannot assume type of `key`.
    """
    assert type(key) == str
    if self.config['separator'] in key:
      return key.split(self.config['separator'])
    else:
      return [key]

  def path_to_key(self, path):
    """
    Function that will transform a path into single key.
    By default, it will join all elements using `separator`.
    Type of path is guaranteed to be a `list`.
    """
    assert type(path) == list
    return self.config['separator'].join(path)

  def key_not_found(self, key, error):
    """
    Override this to return a value in case of key not found error.
    """
    raise error

  def path_not_found(self, path, error):
    """
    Override this to return a value in case of path not found error.
    """
    raise error

  def key_before_get(self, key):
    """
    Override this to modify key before get.
    """
    return key

  def path_before_get(self, path):
    """
    Override this to modify path before get.
    """
    return path

  def value_after_get(self, key, value):
    """
    Override this to modify value before returning.
    """
    return value

  def get(self, path):
    """
    Recursively follows down the path and returns the result found.
    """
    # If path contains only one part
    if len(path) == 1:
      current_key = path[0]
      current_key = self.key_before_get(current_key)
      # Check for built in keys
      if current_key == self.config['self_key']:
        return self
      elif current_key == self.config['parent_key']:
        if self.parent:
          return self.parent
        else:
          return self
      elif current_key == self.config['root_key']:
        return self.root
      elif current_key == self.config['key_key']:
        return self.key
      else:
        try:
          # try to return from store
          value = self.store[current_key]
        except KeyError as e:
          value = self.key_not_found(current_key, e)

        value = self.value_after_get(current_key, value)
        return value
    else:
      # recursion, best thing invented since sliced bread
      return self.get(path[:1]).get(path[1:])

  def __getitem__(self, key):
    """
    Transforms key to path and tries to recursively descent into dict.
    It will also handle relative keys, eg `..` and `...`.
    """
    path = self.key_to_path(copy(key))
    path = self.path_before_get(path)
    try:
      return self.get(path)
    except KeyError as e:
      return self.path_not_found(path, e)

  def key_before_set(self, key):
    """
    Override this to modify key before set.
    """
    return key

  def path_before_set(self, path):
    """
    Override this to modify path before set.
    """
    return path

  def value_before_set(self, current_key, value):
    """
    Override this to modify value before set.
    """
    return value

  def after_set(self):
    pass

  def set(self, path, value):
    """
    Recursively follows down the path until last part using get, and sets
    value in last recursion.
    """
    if len(path) == 1:
      current_key = path[0]
      current_key = self.key_before_set(current_key)
      if isinstance(value, Mapping):
        value = self.__class__(
          __root=self.root,
          __parent=self,
          __key=current_key,
          __config=self.config,
          **value
        )

      value = self.value_before_set(current_key, value)
      self.store[current_key] = value
      self.after_set()
    else:
      self.get(path[:1]).set(path[1:], value)

  def __setitem__(self, key, value):
    """
    Transforms key to path and tries to set value to location of path.
    """
    path = self.key_to_path(copy(key))
    path = self.path_before_set(path)
    self.set(path, value)

  def delete(self, path):
    if len(path) == 1:
      del self.store[path[0]]
    else:
      self.get(path[:1]).delete(path[1:])

  def __delitem__(self, key):
    """
    Transforms key to path and tries to remove value at the location of path.
    """
    path = self.key_to_path(copy(key))
    self.delete(path)

  def contains(self, path):
    if len(path) == 1:
      return path[0] in self.store or path[0] in self.builtin_keys
    else:
      return self.contains(path[:1]) and self.get(path[:1]).contains(path[1:])

  def __contains__(self, key):
    """
    Transforms key to path and tries to check if key exists.
    """
    path = self.key_to_path(copy(key))
    return self.contains(path)

  def __iter__(self):
    """
    Returns paths containing values.
    """
    for key in self.store:
      value = self.store[key]
      if isinstance(value, Mapping):
        for inner_key in value:
          yield self.path_to_key([key, inner_key])
      else:
        yield self.path_to_key([key])

  def __len__(self):
    return sum(1 for _ in self)

  def __unicode__(self):
    return str(self.__class__.__name__) + "\n" + pformat(
      self.to_dict(), indent=2, width=80, compact=False
    )

  def __repr__(self):
    return self.__unicode__()

  def update(self, d):
    """
    Default update method of this dictionary is a deep update.
    """
    for k, v in d.items():
      path = self.key_to_path(copy(k))
      if isinstance(v, Mapping) and k in self:
        self[k].update(v)
      else:
        self[k] = v

  def to_dict(self):
    d = {}
    for key in self.store:
      value = self[key]
      if isinstance(value, RecursiveDict):
        d[key] = value.to_dict()
      else:
        d[key] = value
    return d

  def copy(self):
    return self.__class__(
      __root=self.root,
      __parent=self.parent,
      __key=self.key,
      __config=self.config,
      **self.to_dict()
    )


class InterpolatedDict(RecursiveDict):
  """
  Enables self referential values on top of RecursiveDict.
  By default, it will try to evaluate values containing double curly braces.
  It will also evaluate "<key>" to key of current dictionary level.
  """

  def __init__(self, *args, **kwargs):
    kwargs['__config'] = kwargs.get('__config', {})
    kwargs['__config']['interpolation_regex'] = kwargs['__config'].get(
      'interpolation_regex', r'({{([^{}]*)}})'
    )

    super(InterpolatedDict, self).__init__(*args, **kwargs)

  def value_after_get(self, key, value):
    """
    Tries to interpolate value if there is an instance matching.
    """
    if isinstance(value, str):
      return self.interpolate_value(value)
    else:
      return super(InterpolatedDict, self).value_after_get(key, value)

  def interpolate_value(self, value):
    rgx = re.compile(self.config['interpolation_regex'])
    blocks = rgx.findall(value)
    interpolated_value = value
    for full_block, int_block in blocks:
      full_block_key = self.full_key + self.config['separator'] + int_block
      block_value = self.root[full_block_key]
      if isinstance(block_value, str):
        interpolated_value = interpolated_value.replace(full_block, block_value)
      elif isinstance(block_value, InterpolatedDict):
        interpolated_value = block_value

    return interpolated_value


class ConfDict(InterpolatedDict):
  """
  Adds fallback functionality on top of InterpolatedDict. If current level does
  not contain the key and contains a fallback, this dict will fall back to that
  dictionary with remaining path. If this level does not contain a fallback it
  will try to fallback to parents fallback until it reaches root level.
  """

  def __init__(self, *args, **kwargs):
    kwargs['__config'] = kwargs.get('__config', {})
    kwargs['__config']['fallback_key'] = kwargs['__config'].get(
      'fallback_key', 'fallback'
    )

    super(ConfDict, self).__init__(*args, **kwargs)

  @property
  def has_fallback(self):
    return self.config['fallback_key'] in self.store

  @property
  def fallback(self):
    return self.store[self.config['fallback_key']]

  def key_not_found(self, key, error):
    if key.startswith(
      self.config['fallback_key']
    ) and self.config['separator'] in key and self.has_fallback:
      self.fallback.key = key.split(self.config['separator'])[1]
      return self.fallback

    return super(ConfDict, self).key_not_found(key, error)

  def path_not_found(self, path, error):
    fallback_paths = []

    for idx in range(0, len(path)):
      fallback_path = copy(path)
      fallback_path[idx] = self.config['separator'].join([
        self.config['fallback_key'], fallback_path[idx]
      ])
      fallback_paths.append(fallback_path)

    fallback_paths.reverse()

    for fallback_path in fallback_paths:
      try:
        return self.root.get(fallback_path)
      except KeyError as e:
        pass

    return super(ConfDict, self).path_not_found(path, error)

  def value_after_get(self, key, value):
    # in case fallbacks key was modified before by a fallback access
    if key == self.config['fallback_key']:
      value.key = self.config['fallback_key']

    # do not interpolate if accessed directly as fallback
    if self.config['fallback_key'] in self.full_path:
      return value
    else:
      return super(ConfDict, self).value_after_get(key, value)

  def realize(self, key):
    """
    Realize values if and only if this is a fallback.
    """
    if self.key == 'fallback':
      selfcopy = self.copy()
      self.key = key
      if key in self.parent:
        selfcopy.update(self.parent[key].to_dict())
        self.parent[key] = selfcopy.to_dict()
      else:
        self.parent.update({key: self.to_dict()})
