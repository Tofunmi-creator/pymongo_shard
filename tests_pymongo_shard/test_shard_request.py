import os

import pytest

from pymongo_shard import ShardRequest, ShardInstance  
from tests_pymongo_shard.test_docs._variables import test_variable

ShardInstance.key_file = os.path.join(os.path.dirname(__file__), 'test_docs/_keys.json')

@pytest.fixture
def shard_instance():
    shard_inst = ShardInstance("testshd1")
    shard_inst.key = 'test_key'
    shard_inst.partition = test_variable.set_partition
    shard_inst.save()
    return shard_inst

@pytest.fixture
def shard_request(shard_instance):
    return ShardRequest(shard_instance)

def test_init(shard_request):
    assert shard_request.shard is not None
    assert shard_request.called_methods == {}
    assert shard_request.request_var == {}
    assert shard_request.main_method == {}
    assert shard_request.chain_methods == []

def test_get_method_args(shard_request):
    shard_request.get_method('test_method', 
                             {'test_key': 1}, 
                             {'_id':0,'test_key':1,'user_name':1}
    )
    assert shard_request.main_method['method'] == 'test_method'
    assert shard_request.main_method['args'] == ({'test_key': 1}, {'_id':0,'test_key':1,'user_name':1})
    assert shard_request.main_method['args_type'] == 'args'
    assert shard_request.filter_check()
    assert shard_request.using_shard_partition() 

def test_get_method_kwargs(shard_request):
    shard_request.get_method('test_method', 
                             filter = {'test_key': 1},
                              projection = {'_id':0,'test_key':1,'user_name':1}
    )
    assert shard_request.main_method['method'] == 'test_method'
    assert shard_request.main_method['args'] == {
                                                   'filter':{'test_key': 1}, 
                                                    'projection':{
                                                                  '_id':0,
                                                                  'test_key':1,
                                                                  'user_name':1
                                                    }
    }
    assert shard_request.main_method['args_type'] == 'kwargs'
    assert shard_request.filter_check()

def test_filter_check_document(shard_request):
    shard_request.get_method('test_method', document={'test_key': 34})
    assert shard_request.filter_check()

def test_get_method_args_error(shard_request):
    with pytest.raises(KeyError):
            shard_request.get_method('test_method', 
                                     {'test_key': 1}, 
                                     projection = {'_id':0,'test_key':1,'user_name':1}
            )
    
def test_query_using_partition(shard_request):
    shard_request.get_method('test_method', 
                             {'test_key': 1}, 
                             {'_id':0,'test_key':1,'user_name':1}
    )
    with test_variable.mock_requests():
        result = shard_request.query('test_command')
    assert isinstance(result, list)
    assert len(result) == 1
    assert result == [{'key': '1-10', 'results':['django_results']}]

def test_query_on_keys(shard_request):
    shard_request.get_method('test_method',
                              {}, 
                              {'_id':0,'test_key':1,'user_name':1}
    )
    with test_variable.mock_requests():
        results = shard_request.query('test_command', on_keys=['1-10','11-20'])
    assert len(results) == 2
    for result in results:
        assert result in [
                            {'key': '1-10', 'results':['django_results']},
                            {'key': '11-20', 'results':['fastapi_results']}
    ]
    
def test_query_no_partition_pass(shard_request):
    shard_request.get_method('test_method', {}, {'_id':0,'test_key':1,'user_name':1})
    with test_variable.mock_requests():
        result = shard_request.query('test_command', no_partition_pass=True)
    assert result == None

def test_query_no_shard_partition(shard_request):
    shard_request.get_method('test_method', {}, {'_id':0,'test_key':1,'user_name':1})
    with test_variable.mock_requests():
        results = shard_request.query('test_command',warning=False)
    assert len(results) == 3
    for result in results:
        assert result in  [
                            {'key': '1-10', 'results':['django_results']},
                            {'key': '11-20', 'results':['fastapi_results']},
                            {'key': '21-*', 'results':['flask_results']},
    ]

def test_query_with_status_not_200(shard_request):
    shard_request.get_method('test_method', {}, {'_id':0,'test_key':1,'user_name':1})
    assert not shard_request.filter_check() 
    with test_variable.mock_requests_status_not_200():
        results = shard_request.query('test_command',warning=False)
    results_info = shard_request.get_info() 

    assert results.count([]) == 2
    assert results.count({'key': '11-20', 'results':['fastapi_results']}) == 1
    assert len(results_info) == 3
    for info in results_info:
        assert info in  [    
                            {'status':'failed',
                             'key': '1-10', 
                             'error':'Request failed with status code: 404',
                             'text':'django_error'
                            },
                            {'status':'success',
                             'key': '11-20'
                            },
                            {'status':'failed', 
                             'key': '21-*',
                             'error':'Request failed with status code: 404', 
                             'text':'flask_error'
                            }
        ]
        
def test_query_error_with_status_200(shard_request):
    shard_request.get_method('test_method', {}, {'_id':0,'test_key':1,'user_name':1})
    assert not shard_request.filter_check() 
    with test_variable.mock_requests_error_status_200():
        results = shard_request.query('test_command',warning=False)
    results_info = shard_request.get_info() 
    assert results.count([]) == 2
    assert results.count({'key': '21-*', 'results':['flask_results']}) == 1 
    assert len(results_info) == 3
    for info in results_info:
        assert info in [    
                            {'status':'failed',
                             'key': '1-10', 
                             'error':'Endpoint django error',
                            },
                            {'status':'failed',
                             'key': '11-20',
                             'error':'Endpoint fastapi error'
                            },
                            {'status':'success', 
                             'key': '21-*',
                            }
        ]

def test_data_split(shard_request):
    with test_variable.mock_requests_data_split():
        result = shard_request.data_split(test_variable.data_split_request_source,
                                          test_variable.data_split_request_projection)
    assert result == [{'key': 'test_key',
                       'results':'Split completed. Please review data for consistency between source and partition endpoints'}]

def test_data_split_wrong_key(shard_request):
    with test_variable.mock_requests_data_split():
        with pytest.raises(KeyError):
            shard_request.data_split(test_variable.data_split_request_source_wrong_key,
                                          test_variable.data_split_request_projection)

def test_multi_query():
    query_inst_1 = ShardRequest(ShardInstance("testshd1"))
    query_inst_2 = ShardRequest(ShardInstance("testshd1"))
    query_inst_1.get_method('test_method', 
                            {}, 
                            {'_id':0,'test_key':1,'user_name':1}
    )
    query_inst_2.get_method('test_method', 
                            filter = {'test_key': 15},
                            projection = {'_id':0,'test_key':1,'user_name':1}
    )

    with test_variable.mock_requests():
        query_results_1 = query_inst_1.query('test_command', on_keys=['1-10','11-20'])
        query_results_2 = query_inst_2.query('test_command')

    assert len(query_results_1) == 2
    assert len(query_results_2) == 1
    assert query_results_1 == [ 
                                {'key': '1-10', 'results':['django_results']},
                                {'key': '11-20', 'results':['fastapi_results']}
    ]
    assert query_results_2 == [{'key': '11-20', 'results':['fastapi_results']}]

def test_clear_shards():
    ShardInstance.remove_registered_ids()
