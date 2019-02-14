from hierkeyval import HierarchicalStore
import io
import json

class MockIdentifier:
    pass

def make_identifier(server, channel):
    obj = MockIdentifier()
    obj.server = server
    obj.channel = channel
    return obj


ident = make_identifier('server', 'channel')

def test_store_value():
    HKV = HierarchicalStore(io.StringIO())
    NHKV = HKV.as_namespace('test')
    NHKV.set_val('c', ident, 'key', 3)
    assert NHKV.get_val('c', ident, 'key') == 3
    NHKV.set_val('s', ident, 'key2', 5)
    assert NHKV.get_val('s', ident, 'key2') == 5
    NHKV.set_val('g', ident, 'key3', 7)
    assert NHKV.get_val('g', ident, 'key3') == 7

def test_hierarchical_value():
    HKV = HierarchicalStore(io.StringIO())
    NHKV = HKV.as_namespace('test')
    NHKV.set_val('s', ident, 'key', 10)
    assert NHKV.get_val('csg', ident, 'key') == 10
    NHKV.set_val('g', ident, 'key', 20)
    assert NHKV.get_val('cg', ident, 'key') == 20

def test_saves_after_write():
    f = io.StringIO()
    HKV = HierarchicalStore(f)
    HKV.set_val('s', 'test', ident, 'key', 123)
    f.seek(0)
    obj = json.load(f)
    assert obj[1]['test']['server']['key'] == 123
