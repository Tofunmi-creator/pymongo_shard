import os

import pytest

from pymongo_shard.shard_instance import ShardInstance 
from tests_pymongo_shard.test_docs._variables import test_variable
 
ShardInstance.key_file = os.path.join(os.path.dirname(__file__), 'test_docs/_reigistered_shards.json')


def shard_id_checks(shard_instance, error):
    with pytest.raises(error):
        shard_instance.create_shard('test_key', test_variable.set_partition)

    with pytest.raises(error):
        shard_instance.key = 'test_key'
        shard_instance.partition = test_variable.set_partition
        shard_instance.save()

        
def test_empty_id():
    shard_id_checks(ShardInstance(''), AssertionError)

def test_shard_id_too_long():
    shard_id_checks(ShardInstance('a' * 9), ValueError)

def test_shard_id_not_alphanumeric():
    shard_id_checks(ShardInstance('test$har'), AssertionError)

def test_invalid_partition_key():
    shard_instance = ShardInstance('tstinvd1')
    with pytest.raises(ValueError):
        shard_instance.create_shard('test_key', test_variable.invalid_key_partition)

def test_duplicate_partition_key():
    shard_instance = ShardInstance('tstdup1')
    with pytest.raises(ValueError):
        shard_instance.create_shard('test_key', test_variable.duplicate_key_partition)
        
def test_partition_not_list():
    shard_instance = ShardInstance('tstlst1')
    with pytest.raises(AttributeError):
        shard_instance.create_shard('test_key', test_variable.notlist_partition)


@pytest.fixture
def shard_instance():
    shard_inst = ShardInstance("testshd1")
    return shard_inst


def test_init(shard_instance):
    assert shard_instance.id == "testshd1"
    assert shard_instance.registered_ids is not None

def test_create_shard(shard_instance):
    shard_instance.create_shard('test_key', test_variable.set_partition)
    assert shard_instance.key == 'test_key'
    assert shard_instance.partition is not None
    assert len(shard_instance.partition) == 3


def test_duplicate_shard_id():
    shard_instance = ShardInstance("testshd1")
    with pytest.raises(LookupError):
        shard_instance.create_shard('test_key', test_variable.set_partition)
    

def test_save(shard_instance):
    assert shard_instance.partition == test_variable.get_partition
    shard_instance.partition = test_variable.set_partition_sub
    shard_instance.save()
    ids = ShardInstance.get_registered_ids()
    assert any(shard['id'] == shard_instance.id for shard in ids)
    assert len(shard_instance.partition) == 2
    


def test_register_second_shard():
    shard_inst = ShardInstance("testshd2")
    shard_inst.key = 'test_key2'
    shard_inst.partition = test_variable.set_partition
    shard_inst.save()

def test_get_stored_data():
    shard_instance_1 = ShardInstance("testshd1")
    shard_instance_2 = ShardInstance("testshd2")
    assert shard_instance_1.key == 'test_key'
    assert shard_instance_2.key == 'test_key2'
    assert shard_instance_1.partition == test_variable.get_partition_sub
    assert shard_instance_2.partition == test_variable.get_partition

def test_get_registered_ids():
    ids = ShardInstance.get_registered_ids()
    assert isinstance(ids, list)
    assert len(ids) == 2

def test_get_info(shard_instance):
    info = shard_instance.get_info()
    assert info['id'] == shard_instance.id
    assert shard_instance.partition == test_variable.get_partition_sub

def test_delete(shard_instance):
    shard_instance.delete()
    ids = ShardInstance.get_registered_ids()
    assert not any(shard['id'] == shard_instance.id for shard in ids)
    assert len(ids) == 1


def test_remove_registered_ids():
    ShardInstance.remove_registered_ids()
    ids = ShardInstance.get_registered_ids()
    assert ids == []

