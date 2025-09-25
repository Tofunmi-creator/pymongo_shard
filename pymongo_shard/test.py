import json
import re
import os
from  pymongo import MongoClient
from pymongo.synchronous.collection import Collection
from base import shard

client = MongoClient("localhost", 27017)
db = client['test'] 
lstrv_col= db['list_rev']
#print(lstrv_col.find_one())
char = ['3','dd']
sfind = ['84','9',]
print(len(set(char).intersection(set(sfind))))
os.environ['shard_ids']=json.dumps({'key':'value2'})
shard_ids =json.loads(os.environ['shard_ids'])
print(shard_ids)
print(shard_ids['key'])

new_shard = shard('sii6786')
print(new_shard.key)
#new_shard.partition = [('1-3','http://fdafdsf.com'),('4-8','http://dgsdg.com'),('9-*','https:fsdfsdf.com')]
#new_shard.save()
#new_shard.create_shard('house_id',[('1-3','http://fdafdsf.com'),('4-7','http://dgsdg.com'),('8-*','https:fsdfsdf.com')])

md={}
print(shard.get_registered_ids())