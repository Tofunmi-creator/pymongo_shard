import os
import re
import json


class ShardInstance:
    """Represents a shard instance in the MongoDB sharding system."""

    key_file  = os.path.join(os.path.dirname(__file__), 'registered_shards.json')
    
    @classmethod
    def key_file_check(cls):
        if not os.path.isfile(cls.key_file):
            with open(cls.key_file,'w') as ids:
                ids.write(json.dumps([]))
                ids.close()

    @classmethod
    def get_registered_ids(cls) -> list:
        """Retrieve a list of registered shard IDs.
        
        First, attempts to load the IDs from the 'shard_ids' environment variable.
        If not found or empty, loads the IDs from the 'keys.json' file.
        The loaded IDs are then stored in the 'shard_ids' environment variable.

        Returns:
            list: A list of registered shard IDs.
        """
        cls.key_file_check()
        registered_ids = list()
        if 'shard_ids' in os.environ:
            registered_ids = json.loads(os.environ['shard_ids'])
        if not registered_ids:
            with open(cls.key_file, 'r') as ids:
                registered_ids = json.load(ids)
                ids.close()
            os.environ['shard_ids'] = json.dumps(registered_ids)
        return registered_ids
        

    
    @classmethod
    def remove_registered_ids(cls) -> None:
        """Remove all registered shard IDs.
        Writes an empty list to the 'pymongo_shard/keys.json' file.
        """
        cls.key_file_check()
        with open(cls.key_file, 'w') as ids:
            ids.write(json.dumps([]))
            ids.close()
        if 'shard_ids' in os.environ:
            del os.environ['shard_ids']

    @property
    def partition(self):
        """Get the partition information for this shard instance.

        Returns:
            list: The partition information.
        """
        return self._partition
    
    @partition.setter
    def partition(self, partition: list) -> None:
        """Set the partition information for this shard instance.

        Args:
            partition (list): The partition information.
        """
        if not isinstance(partition, list):
            raise AttributeError(f'Partition must be of type list not type {type(self.partition)}')
        self._partition = []
        self.partition_range=[]
        for partition_info in partition:
            self._partition.append(self.partition_args_check(*partition_info))
    
    
    def __init__(self, shard_id: str) -> None:
        """Initialize a new shard instance.

        Args:
            shard_id (str): The ID of the shard.
        """
        self.id = shard_id 
        self.registered_ids= self.get_registered_ids()
        self.shard_info = list(filter(lambda x: x['id'] == self.id, self.registered_ids))
        if len(self.shard_info) > 0:
            for key, item in self.shard_info[0].items():
                if key =="partition":
                    key="_partition"
                setattr(self,key, item)
                
        
    def create_shard(self, key: str, partition: list) -> None:
        """Create a new shard.

        Args:
            key (str): The key for the shard.
            partition (list): The partition information for the shard.
        """
        self.key = key
        self.partition = partition
        self.id_checks()
        self.register_shard()

    def set_key(self):
        #get collection info
        #check if a key exisits for shard
        pass

    def id_checks(self) -> None:
        """Perform checks on the shard ID.

        Raises:
            ValueError: If the shard ID exceeds 8 characters.
            AssertionError: If the shard ID is not alphanumeric.
            LookupError: If the shard ID already exists.
        """
        if len(self.id)> 8:
            raise ValueError('Shard Id cannot exceed 8 character length')
        if not re.match(r'^[a-zA-Z0-9]+$', self.id):
            raise AssertionError('Shard Id must be alphanumeric characters')
        if len(self.shard_info) > 0:
            raise LookupError(f'Shard ID - {self.id} already exists. Set a non-existing ID for your new shard')
    
    def to_int(self, iterable: list) -> list:
        return list(map(int, iterable))
    
    def partition_args_check(
        self,
        database: str, 
        collection: str, 
        key:str, 
        url:str
    ) -> dict:
        """Check the partition arguments.

        Args:
            database (str): The database name.
            collection (str): The collection name.
            key (str): The partition key.
            url (str): The URL.

        Returns:
            dict: The partition information.

        Raises:
            ValueError: If the partition key is invalid.
        """
        if (not isinstance(database,str)) or (not isinstance(collection, str)):
            raise ValueError('Database and Collection variable must be of type str')
        if re.match(r'^\d+$|^\d+\-(\*|\d+)$', key):
            key_range = re.findall(r'\-?(\d+)', key)
            if self.partition_range:
                duplicate_partition_key = set(self.partition_range).intersection(set(key_range))
                if len(duplicate_partition_key)>0:
                    raise ValueError(f'Duplicate partition key(s) found for {list(duplicate_partition_key)}.')
                if any([i < max(self.to_int(self.partition_range)) for i in self.to_int(key_range)]) :
                    raise ValueError(f'Range containing {key} already exists')  
            self.partition_range.extend(key_range)
            partition_info = {'database':database,'collection':collection,'key': key,'url':url}
            return partition_info
        else:
                raise ValueError(f"Improperly formatted partition key '{key}'. Example of acceptable formats are:'1','2-4','5-*'")

    def register_shard(self, edit: bool = False) -> None:
        """Register the shard.

        Args:
            edit (bool): Whether to edit an existing shard. Defaults to False.
        """
        shard_info = {'id':self.id,'key':self.key,'partition':self._partition}
        if edit:
            shard_index = self.registered_ids.index(self.shard_info[0])
            self.registered_ids[shard_index]=shard_info
        else: 
            self.registered_ids.append(shard_info)
        self.upload_ids()

    def upload_ids(self) -> None:
        """Upload the registered shard IDs to the 'pymongo_shard/keys.json' file.
        """
        with open(self.key_file, 'w') as ids:
            ids.write(json.dumps(self.registered_ids, indent=4))
            ids.close()
        os.environ['shard_ids'] = json.dumps(self.registered_ids)
     
    def get_info(self) -> dict:
        """Get the shard information.

        Returns:
            dict: The shard information.
        """
        return self.shard_info[0]

    def save(self) -> None:
        """Save the shard."""
        if len(self.shard_info) == 0:
            self.id_checks()
            self.register_shard()
        else:
            self.register_shard(edit=True)

    def delete(self) -> None:
        """Delete the shard.

        Raises:
            LookupError: If the shard does not exist.
        """
        try:
            shard_index = self.registered_ids.index(self.shard_info[0])
            self.registered_ids.pop(shard_index)
            self.upload_ids()
        except:
            raise LookupError(f"Shard with ID {self.id} does not exists")
        

       

  



