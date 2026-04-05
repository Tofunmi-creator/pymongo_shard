import pytest
from collections import Counter
from pymongo_shard.data_retriever import Retriever  
from tests_pymongo_shard.test_docs._variables import test_variable

from pymongo_shard.shard_instance import ShardInstance 

@pytest.fixture
def my_mocker(mocker):
    class myMocker(mocker.Mock):   
        def __iter__(self):
            return iter(test_variable.data_split_batch_documents) 
    return myMocker 

@pytest.fixture
def mock_retriever(mocker, my_mocker):
    class test_retriever(Retriever):
        def __init__(self, host: str="localhost", port: int=27017) -> None:
            super().__init__(host, port)
            self.client = mocker.patch('pymongo.MongoClient')
            self.client.__getitem__ =  my_mocker()  #Set up mocker for database as client key value
            self.client.__getitem__.return_value.__getitem__ = my_mocker() #Set up mocker for collection as database key value

    retriever = test_retriever()
    return retriever

def test_client(mock_retriever):
    assert mock_retriever.client is not None
    with pytest.raises(AttributeError):
        mock_retriever.db
    with pytest.raises(AttributeError):
        mock_retriever.col

def test_database(mock_retriever):
    result = mock_retriever.database(test_variable.get_name_db_query)
    assert mock_retriever.client['test_database'] == mock_retriever.db
    mock_retriever.db.name.assert_called_once_with()
    with pytest.raises(AttributeError):
        mock_retriever.col
           
def test_collection_method(mock_retriever):
    mock_retriever.collection(test_variable.find_n_sort_col_query)
    assert mock_retriever.db['test_col'] == mock_retriever.col
    mock_retriever.col.find.assert_called_once_with({'test_key':  12},{'_id': 0})
    mock_retriever.col.find.return_value.sort.assert_called_once_with(-1)

def test_collection_method_kwargs(mock_retriever):
    mock_retriever.collection(test_variable.find_n_sort_col_query_kwargs)
    assert mock_retriever.db['test_col'] == mock_retriever.col
    mock_retriever.col.find.assert_called_once_with(filter={'test_key': 12, 'user_id': 3},projection={'_id': 0, 'user_id': 1})
    mock_retriever.col.find.return_value.sort.assert_called_once_with(-1)
 
def test_ping(mock_retriever):
    assert mock_retriever.ping({'database':'test_database','collection':'test_collection'}) == 'pong'
    assert mock_retriever.client is not None
    assert mock_retriever.client['test_database'] == mock_retriever.db
    assert mock_retriever.db['test_col'] == mock_retriever.col

def test_sys_info(mock_retriever):
    sys_info = mock_retriever.sys_info(test_variable.system_info_query)
    assert 'system' in sys_info['sys_info']
    assert 'memory_info' in sys_info
    assert 'hard_disk_info' in sys_info

def test_data_split(mock_retriever,  mocker):
    with test_variable.mock_requests_send_batch(mocker):
        result = mock_retriever.data_split(test_variable.data_split_endpoint_query())
       

    expected_calls = [
                        mocker.call.find({'$and':[{'test_key':{'$gte':1}},
                                                  {'test_key':{'$lte':10}}
                                                  ]
                                         }, 
                                                {"_id":0,"username":1,"age":1}
                                                                        
                        ),
                        mocker.call.find({'$and':[{'test_key':{'$gte':11}},
                                                    {'test_key':{'$lte':20}}
                                                    ]
                                         }, 
                                         {"_id":0,"username":1,"age":1}
                                                                        
                        ),
                        mocker.call.find({'test_key':{'$gte':21}}, 
                                         {"_id":0,"username":1,"age":1}
                                                                        
                        )
    ]
    
    actual_calls = mock_retriever.col.method_calls
    assert len(actual_calls) == len(expected_calls)
    for call in expected_calls:
        assert call in actual_calls
    assert result == 'Split completed. Please review data for consistency between source and partition endpoints'
    
   
def test_batch_receiver(mock_retriever,  mocker):
    assert len(test_variable.batch_receiver_input_data.keys()) == 3
    for _, request_json in test_variable.batch_receiver_input_data.items():
        for query in request_json:
            mock_retriever.batch_receiver(query)  
    actual_calls = mock_retriever.col.method_calls
    assert len(actual_calls) == 6
    assert actual_calls.count(mocker.call.insert_many(test_variable.data_split_batch_documents[0:3])
    ) == 3
    assert actual_calls.count(mocker.call.insert_many(test_variable.data_split_batch_documents[3:])
    ) == 3
   






    
