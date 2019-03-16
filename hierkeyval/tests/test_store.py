from hierkeyval import HierarchicalStore
import io
import pickle
import pytest

class MockIdentifier:
    pass

def make_identifier(server, channel):
    obj = MockIdentifier()
    obj.server = server
    obj.channel = channel
    return obj


ident = make_identifier('server', 'channel')

def test_store_value():
    HKV = HierarchicalStore(io.BytesIO())
    NHKV = HKV.as_namespace('test')
    NHKV.set_val('c', ident, 'key', 3)
    assert NHKV.get_val('c', ident, 'key') == 3
    NHKV.set_val('s', ident, 'key2', 5)
    assert NHKV.get_val('s', ident, 'key2') == 5
    NHKV.set_val('g', ident, 'key3', 7)
    assert NHKV.get_val('g', ident, 'key3') == 7

def test_hierarchical_value():
    HKV = HierarchicalStore(io.BytesIO())
    NHKV = HKV.as_namespace('test')
    NHKV.set_val('s', ident, 'key', 10)
    assert NHKV.get_val('csg', ident, 'key') == 10
    NHKV.set_val('g', ident, 'key', 20)
    assert NHKV.get_val('cg', ident, 'key') == 20

def test_saves_after_write():
    f = io.BytesIO()
    HKV = HierarchicalStore(f)
    HKV.set_val('s', 'test', ident, 'key', 123)
    f.seek(0)
    obj = pickle.load(f)
    assert obj[1]['test']['server']['key'] == 123

def test_provide_ident_directly():
    HKV = HierarchicalStore(io.BytesIO())
    NHKV = HKV.as_namespace('test')
    NHKV.set_val('s', 'myident', 'key', 5, hasident=True)
    assert NHKV.get_val_ident('s', 'myident', 'key') == 5

def test_delete_value():
    HKV = HierarchicalStore(io.BytesIO())
    NHKV = HKV.as_namespace('test')
    NHKV.set_val('s', ident, 'key', 421)
    assert NHKV.get_val('s', ident, 'key') == 421
    NHKV.del_val('s', ident, 'key')
    with pytest.raises(KeyError):
        NHKV.get_val('s', ident, 'key')

def test_get_default():
    HKV = HierarchicalStore(io.BytesIO())
    NHKV = HKV.as_namespace('test')
    assert NHKV.get_default('c', 'myident', 'key', 123) == 123
    assert NHKV.get_val_ident('c', 'myident', 'key') == 123

def test_set_and_get_global():
    HKV = HierarchicalStore(io.BytesIO())
    NHKV = HKV.as_namespace('test')
    NHKV.set_global('bla', 123)
    assert NHKV.get_val_ident('g', None, 'bla') == 123
    assert NHKV.get_global('bla') == 123

def test_default_doesnt_overwrite():
    HKV = HierarchicalStore(io.BytesIO())
    NHKV = HKV.as_namespace('test')
    NHKV.set_global('bla', 123)
    assert NHKV.get_default('g', None, 'bla', 321) == 123

# Check that transform lambdas are called even on ident functions
def test_ident_functions_store_correctly():
    HKV = HierarchicalStore(io.BytesIO(), {'s': lambda x: x[:2]})
    NHKV = HKV.as_namespace('test')
    NHKV.set_val('s', 'identifier', 'key', 'val', hasident=True)
    # Ensure that the internal identifier is transformed
    assert 'id' in HKV.sserver['test']
