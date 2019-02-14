import io
import json

"""
DO NOT edit objects retrieved
Alternatively, call flush() to ensure changes persisted

The improved version should probably only support custom HDict and HList
objects to prevent this kind of bug
"""
class HierarchicalStore:
    sglobal = {}  # a 'flat' dict
    sserver = {}  # Key is namespace, then serv
    schannel = {}  # Same
    filename = None
    fileobj = None

    def __init__(self, filename_or_obj):
        self.sglobal = {}
        self.sserver = {}
        self.schannel = {}
        if isinstance(filename_or_obj, io.StringIO):
            self.fileobj = filename_or_obj
        elif isinstance(filename_or_obj, str):
            self.filename = filename_or_obj
            # Also attempt to load from file
            try:
                with open(self.filename, 'r') as f:
                    d = json.load(f)
                self.sglobal, self.sserver, self.schannel = d
                if not isinstance(self.sglobal, dict) \
                        or not isinstance(self.sserver, dict) \
                        or not isinstance(self.schannel, dict):
                    # if any of the data is not the right type, reset
                    self.sglobal, self.sserver, self.schannel = {}, {}, {}
            # well, we tried
            except FileNotFoundError:
                pass
            except json.decoder.JSONDecodeError:
                pass
            except TypeError:
                pass  # obj is not a list
            except ValueError:
                pass  # obj has too many/too few elements
        else:
            raise ValueError('filename_or_obj should be a filename or fileobj')
        self.dicts = {'g': self.sglobal, 's': self.sserver, 'c': self.schannel}

    def flush(self):
        if self.filename is None:
            # It's a StringIO obj, truncate
            self.fileobj.truncate(0)
            self.fileobj.seek(0)
            f = self.fileobj
        else:
            f = open(self.filename, 'w')
        json.dump([x for x in self.dicts.values()], f)

    def has_key(self, namespace, mask, key):
        try:
            self.get_val(namespace, mask, key)
            return True
        except KeyError:
            return False

    def get_dict_and_ident(self, level, identifier):
        if level == 'g':
            d = self.sglobal
            ident = None
        elif level == 's':
            d = self.sserver
            ident = identifier.server
        elif level == 'c':
            d = self.schannel
            ident = identifier.channel
        else:
            raise ValueError(f'Param level must be one of g, s, c, but is "{level}".')

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
        raise KeyError(f'Could not find {key} in namespace {namespace}.')

    """
    Set a value.

    :param level: One of 'g', 's', or 'c', the level to store at
    :param namespace: Namespace
    :param identifier: Obj to extract server/channel from
    :param key: The key to store at
    :param val: The value to store
    """
    def set_val(self, level, namespace, identifier, key, val):
        d, ident = self.get_dict_and_ident(level, identifier)
        if namespace not in d:
            d[namespace] = {ident: {}}
        if ident not in d[namespace]:
            d[namespace][ident] = {}
        d[namespace][ident][key] = val
        self.flush()

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

    def set_val(self, level, identifier, key, val):
        return self.hsv.set_val(level, self.namespace, identifier, key, val)


DEFAULT = HierarchicalStore('default.hkv')

def get_default(namespace=None):
    if namespace:
        return NamespacedHStore(DEFAULT, namespace)
    return DEFAULT