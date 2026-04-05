import json
import re
import requests
import warnings
import concurrent.futures

from .shard_instance import ShardInstance


class ShardRequest:
    """A class for making requests to a shard instance.
    """
    def __init__(self, shard_instance: ShardInstance) -> None:
        """Initialize a new ShardRequest instance.

        Args:
            shard_instance (ShardInstance): The shard instance to associate with this request.

        Raises:
            TypeError: If shard_instance is not an instance of ShardInstance.
        """
        if not isinstance(shard_instance, ShardInstance):
            raise TypeError(f'Shard instance must be of type {type(ShardInstance)} not type {type(shard_instance)}')
        self.shard = shard_instance
        self.called_methods = {}
        self.request_var = {}
        self.main_method = {}
        self.chain_methods = []
        
    def get_method(self, method: str, *args,**kwargs) -> 'ShardRequest':
        """Get a method to call on the shard instance.

        Args:
            method (str): The name of the method to call.
            *args: Variable arguments to pass to the method.
            **kwargs: Keyword arguments to pass to the method.

        Returns:
            ShardRequest: This ShardRequest instance.

        Raises:
            KeyError: If both args and kwargs are provided.
        """
        if args and kwargs:
            raise KeyError(
                f"None assigned arguments detected,"
                f"assigned all parameters (e.g., filter={'id':1}) or"
                f"leave them unassigned(e.g.,{'id':1})"
            )

        if not self.main_method:
            self.main_method['method'] = method
            self.main_method['args'] = kwargs or args
            self.main_method['args_type'] = 'kwargs' if kwargs else 'args'
           
        else:
            self.chain_methods.append({'method':method,'args':kwargs or args,
                                       'args_type':'kwargs' if kwargs else 'args' })
        self.called_methods['main_method'] = self.main_method
        self.called_methods['chain_methods'] = self.chain_methods
        return self

    def filter_check(self) -> bool:
        """Check if the filter is valid.

        Returns:
            bool: True if the filter is valid, False otherwise.
        """
        try:
            main_method_args = self.main_method['args']
            if self.main_method['args_type'] == 'args':
                self.filter = main_method_args[0]
            else:
                if 'filter' in  main_method_args:
                    self.filter = main_method_args['filter'] 
                elif 'document' in  main_method_args:
                    self.filter = main_method_args['document']
            filter_value = self.filter[self.shard.key]
            return isinstance(filter_value, int)
        except:
            return False

    def using_shard_partition(self) -> bool:
        """Check if the shard partition is being used.

        Returns:
            bool: True if the shard partition is being used, False otherwise.
        """
        if self.filter_check() and (self._get_partition() in self.shard.partition):
            return True
        return False
    
    def query(self, command: str, 
              on_keys: list = None, 
              warning: bool = True,
              no_partition_pass: bool = False
    ) -> dict:
        """Query the shard.

        Args:
            command (str): The name of the method to call on the Retriever instance via endpoint decorators. 
                           This should match one of the methods on the Retriever class, 
                           such as 'client', 'database', 'collection', 'ping' and 'sys_info'.
            on_keys (list): The keys to query on. If provided, the query will be performed on the specified partitions.
            warning (bool): Whether to warn if the query will be performed on all partitions. Defaults to True.
            no_partition_pass (bool): Whether to return None if no partition is specified. Defaults to False.

        Returns:
            dict | None: The query result, or None if no partition is specified and no_partition_pass is True.
        """

        self.command = command
        if on_keys:
            if not isinstance(on_keys, list):
                raise TypeError(f"Expected type list for on_key argument not type{type(on_keys)}")
            shard_partitions = []
            for key in on_keys:
                key_filter = list(filter(lambda x: x['key'] == key, self.shard.partition))
                if len(key_filter) != 1:
                    raise LookupError(f'Cannot locate partition for key "{key}"')
                shard_partitions.append(key_filter[0])
        
        elif self.using_shard_partition():
            shard_partitions = [self.shard_partition_key]

        elif no_partition_pass:
            return None
        
        else:
            if warning:
                warnings.warn("Query will be performed on all partitions and retrieved data/operation may not be as intended."
                              "Please use the `on_key` parameter to send query to specific endpoint(s) or "
                              "if querying the collection method adjust your `get_method`"
                              "arguments and ensure that `using_partition` method returns a True value"
                )
            shard_partitions = self.shard.partition
        return self.get_data(shard_partitions)

    def data_split(self, shard_source: dict, projection: dict = None) -> dict:
        """Split the data.

        Args:
            shard_source (dict): The shard source data.
            projection (dict): The projection to apply.

        Returns:
            dict: Confirmation of data split success.
        Raises:
            KeyError: If mismatch between source and partition keys.
        """
        shard_info = self.shard.get_info()
        if shard_info['key'] == shard_source['key']:
            self.command = 'data_split'
            shard_source['shard_instance'] = shard_info
            if projection and isinstance(projection, dict):
                shard_source['projection'] = projection
            
            return self.get_data([shard_source])
        else:
            raise KeyError(f"Mismatch between shard and source keys. Shard key is '{shard_info['key']}' not '{shard_source['key']}'")

    def get_data(self,partitions: list) -> list:
        """Get the data from the partition(s).

        Args:
            partitions (list): The partitions to get data from.

        Returns:
            list: The data from the partitions.
        """
        self.query_info = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(partitions)) as executor:
            results = list(executor.map(self.request_data, partitions))
        return results

    def get_info(self) -> list:
        return self.query_info
            
    def _get_partition(self) -> dict | None:
        """Get the partition associated with the filter.

        Returns:
            dict
            The partition associated with the filter, or None if not found.
        """
        shard_partitions = self.shard.partition
        filter_value = self.filter[self.shard.key]
        
        for partition in shard_partitions:
            part_keys = list(map(int,re.findall(r'\-?(\d+)',  partition['key'])))
            self.shard_partition_key = partition
            try:
                if part_keys[0] == filter_value:
                    break
                elif (part_keys[0] < filter_value) and ('*' in partition['key']):
                    break
                elif (part_keys[0] < filter_value <= part_keys[1]):
                    break
                else:
                    self.shard_partition_key = None
            except:
                self.shard_partition_key = None
        return self.shard_partition_key 

    def request_data(self, partition: dict) -> dict | list:
        """Request data from the partition.

        Args:
            partition (dict): The partition to request data from.

        Returns:
            dict | list: The requested data.
        """
        try:
            partition['called_methods'] = self.called_methods
            partition['command'] = self.command
            partition_key = partition['key']
            request_var = self.request_var[partition_key] if partition_key in self.request_var else dict()
            shard_data = requests.post(partition['url'], json=json.dumps(partition), **request_var)
            if shard_data.status_code != 200:
                info={'status':'failed', 'key':partition['key'],'text':shard_data.text,
                      'error':f'Request failed with status code: {shard_data.status_code}'}
                self.query_info.append(info)
                return list()
            else:
                json_return = shard_data.json()
                if 'error' in json_return:
                    info={'status':'failed'}
                    info.update(json_return)
                    self.query_info.append(info)
                    return list()
                elif 'results' in json_return:
                    info = {'status':'success','key':json_return['key']}
                    self.query_info.append(info)
                    return json_return
        except Exception as e:
            self.query_info.append({'status':'failed','key':partition['key'],'error':str(e)})
            return list()
    
    def set_request_var(self, request_var: dict = None) -> None:
        """Set the request variables.

        Args:
            request_var (dict): The request variables to set.
        """
        if request_var:
            partition_keys = [i['key'] for i in self.shard.partition]
            for key, request_vars in  request_var.items():
                if key in partition_keys:
                    if 'json' in request_vars:
                        request_vars.pop('json')
                    if 'url' in request_vars:
                        request_vars.pop('url')
                else:
                    raise LookupError(f'Partition with key {key} not included in shard')
     
        self.request_var = request_var
        


            










