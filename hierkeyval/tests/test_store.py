from hierkeyval import HierarchicalStore
import io
import json


def test_store_value():
    HKV = HierarchicalStore(io.StringIO())
    HKV.set_val('foo', 'c', 'a', 3)
    assert HKV.get_val('foo', '--c', 'a') == 3
    HKV.set_val('foo', 's', 'b', 5)
    assert HKV.get_val('foo', '-s-', 'b') == 5
    HKV.set_val('foo', 'g', 'c', 7)
    assert HKV.get_val('foo', 'g--', 'c') == 7

def test_hierarchical_value():
    HKV = HierarchicalStore(io.StringIO())
    HKV.set_val('foo', 's', 'key', 10)
    assert HKV.get_val('foo', 'gsc', 'key') == 10
    HKV.set_val('foo', 'g', 'key', 20)
    assert HKV.get_val('foo', 'g-c', 'key') == 20

def test_saves_after_write():
    f = io.StringIO()
    HKV = HierarchicalStore(f)
    HKV.set_val('foo', 's', 'key', 123)
    f.seek(0)
    obj = json.load(f)
    assert obj[1]['foo']['key'] == 123
