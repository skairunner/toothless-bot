import io
import os
import pickle

"""
DO NOT edit objects retrieved
Alternatively, call flush() to ensure changes persisted

The improved version should probably only support custom HDict and HList
objects to prevent this kind of bug
"""
class HierarchicalStore:
    filename = None
    fileobj = None

    """
    :param filename_or_obj: A filename or a fileobj to persist in
    :param transforms: Any additional transforms for ident parsing
    """
    def __init__(self, filename_or_obj, transforms={}, is_default=False):
        self.sglobal = {}
        self.sserver = {}
        self.schannel = {}
        self.ident_transforms = {
            'g': lambda x: x,
            's': lambda x: x,
            'c': lambda x: x
        }
        self.ident_transforms.update(transforms)
        if isinstance(filename_or_obj, io.BytesIO):
            self.fileobj = filename_or_obj
        elif isinstance(filename_or_obj, str):
            self.filename = filename_or_obj
            # Also attempt to load from file
            try:
                with open(self.filename, 'rb') as f:
                    d = pickle.load(f)
                self.sglobal, self.sserver, self.schannel = d
                if not isinstance(self.sglobal, dict) \
                        or not isinstance(self.sserver, dict) \
                        or not isinstance(self.schannel, dict):
                    # if any of the data is not the right type, reset
                    self.sglobal, self.sserver, self.schannel = {}, {}, {}
            # well, we tried
            except FileNotFoundError:
                pass
            except pickle.UnpicklingError:
                pass
            except TypeError:
                pass  # obj is not a list
            except ValueError:
                pass  # obj has too many/too few elements
        else:
            raise ValueError('filename_or_obj should be a filename or fileobj')
        self.dicts = {'g': self.sglobal, 's': self.sserver, 'c': self.schannel}

        if is_default:
            global DEFAULT
            DEFAULT = self

    def flush(self):
        if self.filename is None:
            # It's a BytesIO obj, make new
            f = io.BytesIO()
            f = self.fileobj
        else:
            head, tail = os.path.split(self.filename)
            swppath = os.path.join(head, '.__' + tail)
            f = open(swppath, 'wb')
        pickle.dump([x for x in self.dicts.values()], f)
        # If success, swap files
        if isinstance(f, io.BytesIO):
            self.fileobj.truncate(0)
            self.fileobj.seek(0)
            f.seek(0)
            self.fileobj.write(f.read())
        else:
            # Swap files
            os.replace(swppath, self.filename)

    def get_dict_and_ident(self, level, identifier=None):
        ident = None
        if level == 'g':
            d = self.sglobal
        elif level == 's':
            d = self.sserver
            if identifier:
                ident = self.ident_transforms['s'](identifier.server)
        elif level == 'c':
            d = self.schannel
            if identifier:
                ident = self.ident_transforms['c'](identifier.channel)
        else:
            raise ValueError(f'Param level must be one of g, s, c, but is "{level}".')

        return d, ident

    # Does not attempt to extract identifier from a msg.
    def get_dict_and_ident_direct(self, level, identifier=None):
        if level == 'g':
            d = self.sglobal
            ident = None
        elif level == 's':
            d = self.sserver
            ident = self.ident_transforms['s'](identifier)
        elif level == 'c':
            d = self.schannel
            ident = self.ident_transforms['c'](identifier)
        return d, ident

    """
    Checks levels in order from start to end,returning the first level's value found
    Valid levels are g, s, c for global, server and channel, respectively.

    :param namespace: Since HStore is by plugin, specify namespace
    :param levels: The levels to check
    :param identifier: The object to extract server/channel from
    :param key: The key to get the value for.
    """
    def get_val(self, levels, namespace, identifier, key):
        for level in levels:
            d, ident = self.get_dict_and_ident(level, identifier)
            try:
                return d[namespace][ident][key]
            except KeyError:
                continue
            except TypeError:
                continue
        raise KeyError(
            f'Could not find key {key} with ident {ident}, '
            f'namespace {namespace}, level {level}')

    """
    Like get_val but always using one ident
    """
    def get_val_ident(self, level, namespace, ident, key):
        d, ident = self.get_dict_and_ident_direct(level, ident)
        try:
            return d[namespace][ident][key]
        except KeyError:
            pass
        except TypeError:
            pass
        raise KeyError(
            f'Could not find key {key} with ident {ident}, '
            f'namespace {namespace}, level {level}')

    """
    Like get_val_ident but provides a default.
    """
    def get_default(self, level, namespace, ident, key, default):
        try:
            return self.get_val_ident(level, namespace, ident, key)
        except KeyError:
            self.set_val(level, namespace, ident, key, default, hasident=True)
            return default
    """
    Set a value.

    :param level: One of 'g', 's', or 'c', the level to store at
    :param namespace: Namespace
    :param identifier: Obj to extract server/channel from, or an ident
    :param key: The key to store at
    :param val: The value to store
    :param hasident: If True, will use ident without processing it
    """
    def set_val(self, level, namespace, identifier, key, val, hasident=False):
        if hasident:
            d, ident = self.get_dict_and_ident_direct(level, identifier)
        else:
            d, ident = self.get_dict_and_ident(level, identifier)

        if namespace not in d:
            d[namespace] = {ident: {}}
        if ident not in d[namespace]:
            d[namespace][ident] = {}
        d[namespace][ident][key] = val
        self.flush()

    def del_val(self, level, namespace, identifier, key, hasident=False):
        if hasident:
            d, ident = self.get_dict_and_ident(level, identifier)
        else:
            d, ident = self.get_dict_and_ident(level, identifier)

        if namespace not in d:
            d[namespace] = {ident: {}}
        val = None
        if ident in d[namespace]:
            val = d[namespace][ident]
            del d[namespace][ident]
        self.flush()
        return val

    def as_namespace(self, namespace):
        return NamespacedHStore(self, namespace)


"""
Convenience wrapper on HSV for get/set that has a namespace set at creation
"""
class NamespacedHStore:
    def __init__(self, HSV, namespace):
        self.hsv = HSV
        self.namespace = namespace

    def get_val(self, levels, identifier, key):
        return self.hsv.get_val(levels, self.namespace, identifier, key)

    def get_global(self, key):
        return self.hsv.get_val_ident('g', self.namespace, None, key)

    def get_val_ident(self, level, ident, key):
        return self.hsv.get_val_ident(level, self.namespace, ident, key)

    def set_val(self, level, identifier, key, val, hasident=False):
        return self.hsv.set_val(level, self.namespace, identifier, key, val, hasident)

    # Removes the need for an identifier because global does not have one
    def set_global(self, key, val):
        return self.hsv.set_val('g', self.namespace, None, key, val, True)

    def del_val(self, level, identifier, key, hasident=False):
        return self.hsv.del_val(level, self.namespace, identifier, key, hasident)

    def get_default(self, level, ident, key, default):
        return self.hsv.get_default(level, self.namespace, ident, key, default)

    def flush(self):
        return self.hsv.flush()


DEFAULT = None
def get_default(namespace=None):
    global DEFAULT
    if DEFAULT is None:
        DEFAULT = HierarchicalStore(
            'default.hkv',
            transforms={'s': lambda x: x.id, 'c': lambda x: x.id},
            is_default=True
        )

    if namespace:
        return DEFAULT.as_namespace(namespace)
    return DEFAULT
