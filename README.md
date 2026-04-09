# pymongo_shard

![PyPI version](https://img.shields.io/pypi/v/pymongo_shard.svg)


* PyPI package: https://pypi.org/project/pymongo-shard/
* Free software: MIT License
* Source Code: [https://github.com/Tofunmi-creator/pymongo_shard](https://github.com/Tofunmi-creator/pymongo_shard)


<br>

Pymongo_shard is a Python package designed for pymongo developers to extract data from server shards (endpoints) running pymongo, the official <a href = "https://github.com/mongodb/mongo-python-driver/">Python MongoDB driver</a>. It's perfect for handling data computing and storage constraints by horizontally sharding data across multiple servers, providing a single point for querying. The package offers modules that streamline data retrieval via API requests, allowing developers to write queries similar to those used with the pymongo package.

---
## Installation

Create and activate a virtual environment and then install pymongo_shard:

<div class="termy">

```console
$ pip install  pymongo_shard

```

</div>

---
## Usage

### ShardInstance

```Python
from pymondo_shard import ShardInstance


shard_id = 'shard_id'
shard_key = 'shard_key'
partition = [
    ('endpoint1_database', 'endpoint1_collection', 'endpoint1_partition_key','endpoint1_url'),
    ('endpoint2_database', 'endpoint2_collection', 'endpoint2_partition_key','endpoint2_url'),
    ('endpoint2_database', 'endpoint3_collection', 'endpoint3_partition_key','endpoint3_url')
]

# Create a shard instance using the create shard method or by declaring attribute variables and save method

shard = ShardInstance(shard_id)
shard.create_shard(shard_key, partition)

          ----------- OR -------------

shard = ShardInstance(shard_id)
shard.key = shard_key
shard.partition = partition
shard.save()

"""
Note:  Partition keys use a special format and not adhering to this format will throw errors. 
       Examples include '1', '2-10', '11-*', etc. Typically, partition keys are integers, 
       range of two integers, or integer to asterisk sign representing an unbounded end of a range, 
       all represented as string characters.
"""
```


### ShardRequest

```Python
from pymondo_shard import ShardInstance, ShardRequest

shard_request = ShardRequest(ShardInstance(shard_id))


# To perform a find query using pymongo, you would write:
# pymongo_collection.find({'shard_key':3},{'_id':0,'shard_key':1,'name':1}).sort({'name':1})

# Here, you will write the same query as:

shard_request.get_method('find',{'shard_key':3},{'_id':0,'shard_key':1,'name':1}).get_method('sort',{'name:1})

# If you have properly configured your partition keys, the query algorithm is able to
# automatically direct your query to the corresponding partition (endpoint), otherwise the query will
# be directed to all partitions (default).

shard_request.query('collection')

# However, you can check if your query will be directly to the right partition with the
# `using_partition` method below.

shard_request.using_partition()

# To direct query to specific partitions, set the on_keys parameter to a list of specified
# partition keys as shown below.

shard_request.query('collection', on_keys=['1','2-10'])

```


### Endpoints
The endpoints are used to handle queries and data retrieval from your shard instance partitions. They cover three of the most used python API/web packages: FastAPI, Flask and Django Rest Framework. It is developer's responsibility to ensure that these packages are installed and properly configured prior to using the endpoints. This package must also be installed on every endpoint server.

```Python

# FastAPI endpoint
from fastapi import FastAPI, Request
from pymongo_shard.endpoints import endpoint_fastapi

app = FastAPI()

@app.post("path/")
@endpoint_fastapi(Request, host='host_url', port='host_url')
def fastapi_response(request:Request, response:dict):   
    return response


# Flask endpoint
from flask import Flask, request
from pymongo_shard.endpoints import endpoint_flask

app = Flask(__name__)

@app.route('/path/', methods=['GET', 'POST'])
@endpoint_flask(request, host='host_url', port='host_url')
def flask_response(response=None):
    return json.dumps(response)


# Django endpoint
#In your views.py file
from rest_framework.decorators import api_view
from pymongo_shard.endpoints import endpoint_django

@api_view(['GET','POST'])  
@endpoint_django(host='host_url', port='host_url')
def django_view(request, **kwargs):
    return Response(kwargs)


# However response from endpoints may not be as intended, for example when you call the find method
# on a pymongo collection instance you will get a pymongo.synchronous.cursor.Cursor object as the
# return value (e.g., <pymongo.synchronous.cursor.Cursor object at 0x0x0x0x0x>),
# and an error describing the response as not json serializable.
# In these situations, you can access the method(s) called on the endpoint's collection instance
# via the `shard_method` module and then handle the response using the appropriate technique.


# FastAPI endpoint
from pymongo_shard.endpoints import endpoint_fastapi, shard_method as sm

@app.post("path/")
@endpoint_fastapi(Request, host='host_url', port='host_url')
def fastapi_response(request:Request, response:dict):
    sh_md = sm(request,endpoint='fastapi')
    if sh_md.main() == 'find':
        response['results']= list(response['results'])
    return response


# For flask and django endpoints, update the shard_method's enpoint parameter to 'flask' and 'django' respectively.
# To access chain methods such as 'sort','limit', and so on, use `sm.chain()` method.

```


### Splitting Data
This package also provides a method to split data across partitions present in your shard instance. To split data, place the appropriate endpoint decorator as shown above in the server script where the source data is located. Ensure that no authentication or permission restriction is applied to partition endpoints when calling this method. To query data with authentication restrictions see the `set_request_var` method below.

```Python
from pymondo_shard import ShardInstance, ShardRequest

shard_request = ShardRequest(ShardInstance(shard_id))

source_endpoint = {
                    'database': 'source_database',
                    'collection': 'source_collection',
                    'key': 'shard_key',
                    'url': 'source_endpoint_url'
}
# Note: Source key must match with shard instance key

# The optional projection parameter represents data fields at your source endpoint you'd like query and send to partition endpoints.
projection = {
               'name':1,
               'age':1,
}

# Call data split method
shard_request.data_split(source_endpoint, projection)

```

### Setting requests parameters
You are permitted to set requests parameters per partition with the exception of `url` and `json` parameters. For instance, you may have authentication restrictions applied to a partition endpoint and want to set the requests headers parameter (see example below).

```Python
from pymondo_shard import ShardInstance, ShardRequest

shard_request = ShardRequest(ShardInstance(shard_id))

source_endpoint = {
                    'database': 'source_database',
                    'collection': 'source_collection',
                    'key': 'shard_key',
                    'url': 'source_endpoint_url'
}

token = '************'
headers = {
    "Authorization": f"Token {token}",
    "Content-Type": "application/json"
}
shard_request.set_request_var(
                                {
                                  'endpoint1_partition_key':{'headers':headers}
                                }                          
)

shard_request.query('collection')

# Here, we set the requests headers parameter for endpoint1 using its endpoint1_partition_key (e.g., '1-10').
```



---
## License

This project is licensed under the terms of the MIT license.

## Credits

This package was created with [Cookiecutter](https://github.com/audreyfeldroy/cookiecutter) and the [audreyfeldroy/cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage) project template.









