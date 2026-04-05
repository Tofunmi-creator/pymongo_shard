import json
from contextlib import contextmanager
import copy
import requests_mock


class test_variable:

    set_partition = [
                    ("test", "django", "1-10", "http://test_url_django"),
                    ("test", "fastapi", "11-20", "http://test_url_fastapi"),
                    ("test", "flask", "21-*", "http://test_url_flask")
    ]

    set_partition_sub = [
                        ("test", "django", "1-10", "http://test_url_django"),
                        ("test", "fastapi", "11-20", "http://test_url_fastapi")
    ]

    get_partition = [
                        {
                            "database": "test",
                            "collection": "django",
                            "key": "1-10",
                            "url": "http://test_url_django"
                        },
                        {
                            "database": "test",
                            "collection": "fastapi",
                            "key": "11-20",
                            "url": "http://test_url_fastapi"
                        },
                        {
                            "database": "test",
                            "collection": "flask",
                            "key": "21-*",
                            "url": "http://test_url_flask"
                        }
    ]

    get_partition_sub = [
                        {
                            "database": "test",
                            "collection": "django",
                            "key": "1-10",
                            "url": "http://test_url_django"
                        },
                        {
                            "database": "test",
                            "collection": "fastapi",
                            "key": "11-20",
                            "url": "http://test_url_fastapi"
                        },
                    
    ]
    
    invalid_key_partition = [
                                {
                                    "database": "test",
                                    "collection": "django",
                                    "key": "edceid",
                                    "url": "http://test_url_django"
                                },
    ]

    duplicate_key_partition = [
                                {
                                    "database": "test",
                                    "collection": "django",
                                    "key": "1-10",
                                    "url": "http://test_url_django"
                                },
                                {
                                    "database": "test",
                                    "collection": "fastapi",
                                    "key": "8",
                                    "url": "http://test_url_fastapi"
                                },
    ]

    notlist_partition = (
                                {
                                    "database": "test",
                                    "collection": "django",
                                    "key": "1-10",
                                    "url": "test_url_django"
                                },
                                {
                                    "database": "test",
                                    "collection": "fastapi",
                                    "key": "8",
                                    "url": "test_url_fastapi"
                                },
    )

    find_n_sort_col_query = {'command':'collection',
                             'database': 'test_db', 
                             'collection': 'test_col', 
                             'called_methods': { 'main_method': {'method': 'find', 
                                                                'args': [{'test_key':12},{'_id':0}], 
                                                                'args_type': 'args'
                                                                }, 
                                                'chain_methods': [{'method':'sort',
                                                                    'args':[-1],
                                                                    'args_type': 'args'
                                                                }]
                                            }
    }

    find_n_sort_col_query_kwargs = {'command':'collection',
                             'database': 'test_db', 
                             'collection': 'test_col', 
                             'called_methods': { 'main_method': {'method': 'find', 
                                                                'args': {'filter':{'test_key':12,'user_id':3},'projection':{'_id':0, 'user_id':1}}, 
                                                                'args_type': 'kwargs'
                                                                }, 
                                                'chain_methods': [{'method':'sort',
                                                                    'args':[-1],
                                                                    'args_type': 'args'
                                                                }]
                                            }
    }

    client_query = {'command':'client',
                    'database': 'test_db', 
                    'collection': 'test_col', 
                    'called_methods': { 'main_method': {'method': 'admin.command', 
                                                                'args': ['serverStatus'], 
                                                                'args_type': 'args'
                                                                }, 
                                        'chain_methods': []
                                            }
    }

    get_name_db_query = {'command':'client',
                         'database': 'test_db', 
                         'collection': 'test_col', 
                         'called_methods': { 'main_method': {'method': 'name', 
                                                            'args': [], 
                                                            'args_type': 'args'
                                                            }, 
                                            'chain_methods': []
                                        }
    }
    
    system_info_query = {'command':'sys_info',
                         'database': 'test_db', 
                         'collection': 'test_col', 
                         'called_methods': {'main_method': [], 
                                            'chain_methods': []
                                        }
    }

    data_split_request_source = {"database": "test",
                                 "collection": "source",
                                 "key": "test_key",
                                 "url": "http://test_url_source"
    }

    data_split_request_source_wrong_key = {"database": "test",
                                         "collection": "source",
                                         "key": "wrong_key",
                                         "url": "http://test_url_source"
    }
    
    data_split_request_projection = { "username":1,
                                      "age":1

    }

    data_split_batch_documents = [{"user":1}, {"user_id":2}, {"user_id":3},
                                  {"user_id":4}, {"user_id":5}, {"user_id":6}]

    batch_receiver_input_data = {}


    @staticmethod
    @contextmanager
    def mock_requests():
        with requests_mock.Mocker() as m:
            m.post("http://test_url_django", 
                   json = {'key': '1-10', 'results':['django_results']}, 
                   status_code=200)
            m.post("http://test_url_fastapi", 
                   json = {'key': '11-20', 'results':['fastapi_results']}, 
                   status_code=200)
            m.post("http://test_url_flask", 
                   json = {'key': '21-*', 'results':['flask_results']}, 
                   status_code=200)
            yield

    @staticmethod
    @contextmanager
    def mock_requests_status_not_200():
        with requests_mock.Mocker() as m:
            m.post("http://test_url_django", 
                    status_code = 404, 
                    text = 'django_error')
            m.post("http://test_url_fastapi", 
                    json = {'key': '11-20', 'results':['fastapi_results']}, 
                    status_code = 200)
            m.post("http://test_url_flask", 
                    status_code = 404,
                    text = 'flask_error')
            yield

    
    @staticmethod
    @contextmanager
    def mock_requests_error_status_200():
        with requests_mock.Mocker() as m:
            m.post("http://test_url_django", 
                    json = {'key': '1-10', 'error':'Endpoint django error'}, 
                    status_code = 200)
            m.post("http://test_url_fastapi", 
                    json = {'key': '11-20', 'error':'Endpoint fastapi error'}, 
                    status_code = 200)
            m.post("http://test_url_flask", 
                    json = {'key': '21-*', 'results':['flask_results']},
                    status_code = 200)
            yield

    @staticmethod
    @contextmanager
    def mock_requests_data_split():
        with requests_mock.Mocker() as m:
            m.post("http://test_url_source", 
                   json = {'key': 'test_key', 
                           'results':'Split completed. Please review data for consistency between source and partition endpoints'}, 
                   status_code=200)
            yield

    @staticmethod
    def data_split_endpoint_query():
        source = {"command":"data_split",
                  "database": "test",
                  "collection": "source",
                  "key": "test_key",
                  "url": "http://test_url_source",
        }
        source.update(test_variable.data_split_request_source)
        source['projection'] = test_variable.data_split_request_projection
        shard_instance = {"id":"testshd1","key":"test_key"}
        shard_instance['partition'] = copy.deepcopy(test_variable.get_partition)
        source['shard_instance'] = shard_instance
        return source
  
    @staticmethod
    @contextmanager
    def mock_requests_send_batch(mocker):
        with requests_mock.Mocker() as m:
            mocker_dumps = mocker.patch('sys.getsizeof')
            mocker_dumps.return_value = 20000000
            m.post("http://test_url_django", 
                    json = {'results':"None"}, 
                    status_code = 200)
            m.post("http://test_url_fastapi", 
                    json = {'results':"None"}, 
                    status_code = 200)
            m.post("http://test_url_flask", 
                    json = {'results':"None"}, 
                    status_code = 200)
            yield m
            for request in m.request_history:
                request_json = json.loads(request.json())
                request_key = request_json["key"]
                test_variable.batch_receiver_input_data.setdefault(request_key, []) 
                test_variable.batch_receiver_input_data[request_key].append(request_json)
    
      

