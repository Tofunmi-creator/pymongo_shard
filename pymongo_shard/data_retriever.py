import json
import math
import platform
import psutil
import re
import requests
import sys
import threading

from typing import Any

from  pymongo import MongoClient




class Retriever():
    """A class for retrieving data through a pymongo instance.
    """
    def __init__(self, host: str="localhost", port: int=27017) -> None:
        """Initialize a new Retriever instance.

        Args:
            host (str): The hostname or IP address of the pymongo instance.
            port (int): The port number of the pymongo instance.
        """
        self.client = MongoClient(host, port)
        
    def ping(self, query: dict) -> str:
        """Ping the pymongo instance.

        Args:
            query (dict): The query to send to the pymongo instance.

        Returns:
            str: 'pong'
        """
        try:
            self.db = self.client[query['database']]
            self.col = self.db[query['collection']]
        except:
            return 'Not Available'
        return 'pong'

    def _get_size(self, bytes: int, suffix: str="B") -> str:
        """Scale bytes to its proper format.

        Args:
            bytes (int): The number of bytes.
            suffix (str): The suffix to use.

        Returns:
            str: The scaled bytes.
        """
        factor = 1024
        for unit in ["", "K", "M", "G", "T", "P"]:
            if bytes < factor:
                return f"{bytes:.2f}{unit}{suffix}"
            bytes /= factor

    def sys_info(self, query: dict) -> dict:
        """Get system information about the pymongo instance.

        Args:
            query (dict): The query to send to the pymongo instance.

        Returns:
            dict: System information about the hardware running pymongo instance.
        """
        uname = platform.uname()
        svmem = psutil.virtual_memory()
        partitions = psutil.disk_partitions()

        sys_info = {
                    "system": uname.system,"node_name": uname.node,
                    "release": uname.release, "version": uname.version, 
                    "machine":uname.machine, "processor":uname.processor,
                    "physical_cores": psutil.cpu_count(logical=False),
                    "total_cores":psutil.cpu_count(logical=True),
                   }

        memory_info = {
                        "total": self._get_size(svmem.total),
                        "available": self._get_size(svmem.available),
                        "used": self._get_size(svmem.used),
                        "percentage": f"{svmem.percent}%"
                      }
        
        hard_disk_info = []
        
        for partition in partitions:
            partition_info = {
                                "device": {partition.device},
                                "mountpoint": {partition.mountpoint},
                                "file_system_type": {partition.fstype}
                             }
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
            except PermissionError:
                continue
            partition_info.update({"total_size": self._get_size(partition_usage.total)})
            partition_info.update({"used": self._get_size(partition_usage.used)})
            partition_info.update({"free": self._get_size(partition_usage.free)})
            partition_info.update({"percentage": f"{partition_usage.percent}%"})
            hard_disk_info.append(partition_info)
        
        server_info = {
                        "sys_info": sys_info,
                        "memory_info":memory_info,
                        "hard_disk_info": hard_disk_info
                      }
        return server_info
        
    def client(self, query: dict) -> Any:
        """Get a client instance.

        Args:
            query (dict): The query to send to the pymongo instance.

        Returns:
            Any: Results from calling pymongo client instance method(s).
        """
        instance = self.client
        return self._method_results(instance,query)

    def database(self, query: dict) -> Any:
        """Get a database instance.

        Args:
            query (dict): The query to send to the pymongo instance.

        Returns:
            Any: Results from calling pymongo database instance method(s).
        """
        self.db = self.client[query['database']]
        return self._method_results(self.db,query) 

    def collection(self, query: dict) -> Any:
        """Get a collection instance.

        Args:
            query (dict): The query to send to the pymongo instance.

        Returns:
            Any: Results from calling pymongo collection instance method(s).
            
        """
        self.db = self.client[query['database']]
        self.col = self.db[query['collection']]
        return self._method_results(self.col,query)
    
    def _result_var(self, instance: Any, method_dict: dict) -> Any:
        """Get the result of a method call.

        Args:
            instance (object): The instance to call the method on.
            method_dict (dict): The method to call.

        Returns:
            object: The result of the method call.
        """
        if '.' in method_dict['method']: 
            methods = method_dict['method'].split('.')
            for method in methods:
                instance = getattr(instance,method)
            if method_dict['args_type'] == 'kwargs':
                return instance(**method_dict['args'])
            else:
                return instance(*method_dict['args'])
        else:
            if method_dict['args_type'] == 'kwargs':
                return getattr(instance, method_dict['method'])(**method_dict['args'])
            else:
                return getattr(instance, method_dict['method'])(*method_dict['args'])

    def _method_results(self, instance: Any, query: dict) -> Any:
        """Execute a sequence of methods on the given instance.

        Args:
            instance (object): The instance to execute the methods on.
            query (dict): A dictionary containing the methods to execute. It should have the following structure:
                {
                    'called_methods': {
                        'main_method': {'method': str, 'args': list or dict, 'args_type': str},
                        'chain_methods': list of {'method': str, 'args': list or dict, 'args_type': str}
                    }
                }

        Returns:
            Any: The result of the last method executed.

        Note:
            The 'args_type' key in the method dictionary should be either 'args' or 'kwargs', 
            indicating whether the method arguments are positional or keyword arguments.
        """
        called_methods = query['called_methods']
        main_method = called_methods['main_method']
        results =  self._result_var(instance,main_method)
        chain_methods =  called_methods['chain_methods']
        if len(chain_methods) > 0:
            for chain_method in chain_methods:
                results =  self._result_var(results,chain_method)
        return results
    
    def data_split(self, query: dict) -> str:
        """Split data into partitions.

        Args:
            query (dict): The query to send to the pymongo instance.

        Returns:
            str: A message indicating that the data
        """
        # Set up database and collection
        self.db = self.client[query['database']]
        self.col = self.db[query['collection']]

        shard_instance = query['shard_instance']
        partitions = shard_instance['partition']
        shard_key = shard_instance['key']
      
        query.setdefault('projection', {})
        query['projection'].update({"_id":0})
        projection =  query['projection']

        key_values = []

        for partition in partitions:
            key = partition['key']
            key_range = [int(i) for i in re.findall(r'\-?(\d+)', key)]
            key_values.extend(key_range)
            if "*" not in key:
                if len(key_range) == 1:
                    find_query = ({shard_key:key_range[0]},projection)
                elif len(key_range) == 2:
                    key_range.sort()
                    find_query = ({'$and':[{shard_key:{'$gte':key_range[0]}},{shard_key:{'$lte':key_range[1]}}]},projection)
            else:
                if len(key_range) == 1:
                    find_query = ({shard_key:{'$gte':key_range[0]}},projection)
                else:
                    find_query = ({shard_key:{'$gt':max(key_values)}},projection)
            
            documents = list(self.col.find(*find_query))

            self._send_batch(documents, partition)
        return 'Split completed. Please review data for consistency between source and partition endpoints'

    def _send_batch(self, documents: list, partition: dict) -> None:
        """Send a batch of documents to a partition.

        Args:
            documents (list): The documents to send.
            partition (dict): The partition to send the documents to.
        """
        doc_size = sys.getsizeof(documents) / (10**6) #size in mb
        transfer_size = 10  
        batch_no = math.ceil(doc_size/transfer_size)
        elem_batch = math.ceil(len(documents)/batch_no)
        count = 1
        batch_start = 0
        while count <= batch_no:
            batch_end = batch_start + elem_batch
            if count == batch_no:
                batch = documents[batch_start:]
            else:
                batch = documents[batch_start:batch_end]
            batch_start += elem_batch
            count += 1
            partition['called_methods'] = {
                                            'main_method':{'method':'insert_many',
                                                            'args':[batch],
                                                            'args_type':'args'
                                                          },
                                                            'chain_methods':list()
                                          }
            partition['command'] = 'batch_receiver'     
            if batch:
               requests.post(partition['url'], json=json.dumps(partition)).json()
               
    def batch_receiver(self, query: dict) -> None:
        """Receive a batch of documents.

        Args:
            query (dict): The query to send to the pymongo instance.
        """
        thread_batch = threading.Thread(target=self.collection, args=(query,),daemon=True)
        thread_batch.start()
        
   

        
    

            
    




