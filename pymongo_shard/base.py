import os
import re
import json


class shard:
    @classmethod
    def get_registered_ids(cls):
        try:
            with open('pymongo_shard/keys.json', 'r') as ids:
                registered_ids= json.load(ids)
        except:
            registered_ids={}
        return registered_ids

    def __init__(self, shard_id):
        self.id = shard_id 
        self.registered_ids= self.get_registered_ids()
        if self.id in self.registered_ids:
            for key, item in self.registered_ids[shard_id].items():
                setattr(self,key, item)
                
        
    def create_shard(self,key, partition):
        self.key = key
        self.partition = partition
        self.id_checks()
        self.partition_checks()
        self.register_shard()

    def set_key(self):
        #get collection info
        #check if a key exisits for shard
        pass
    def id_checks(self):
        if len(self.id)> 8:
            raise ArithmeticError('Shard Id cannot exceed 8 character length')
        if not re.match(r'^[a-zA-Z0-9]+$', self.id):
            raise AssertionError('Shard Id must be alphanumeric characters')
        if self.id in self.registered_ids:
            raise LookupError(f'Shard ID - {self.id} already exists. Set a non-existing ID for your new shard')

    def partition_checks(self):
        if not isinstance(self.partition, list):
            raise AssertionError(f'Partition must be of type dict not type {type(self.partition)}')
        partition_range = []
        for partition_info in self.partition:
            key= partition_info[0]
            if re.match(r'^\d+$|^\d+\-(\*|\d+)$', key):
                key_range = re.findall(r'\-?(\d+)', key)
                duplicate_partition_key = set(partition_range).intersection(set(key_range))
                if len(duplicate_partition_key)>0:
                    raise ValueError(f'Duplicate partition key(s) found for {list(duplicate_partition_key)}.')
                partition_range.extend(re.findall(r'\-?(\d+)', key))
            else:
                raise ValueError(f"Improperly formatted partition key '{key}'. Example of acceptable formats are:'1','2-4','5-*'")

    def register_shard(self):
        shard_info = {'id':self.id,'key':self.key,'partition':self.partition}
        self.registered_ids[self.id]=shard_info
        with open('pymongo_shard/keys.json', 'w') as ids:
            ids.write(json.dumps(self.registered_ids, indent=4))
        os.environ['shard_ids']=json.dumps(self.registered_ids)
     

    def save(self):
        if self.id not in self.registered_ids:
            self.id_checks()
        self.partition_checks()
        self.register_shard()
       

        


