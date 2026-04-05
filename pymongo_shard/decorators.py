import json
from asgiref.sync import async_to_sync

from pymongo_shard.data_retriever import Retriever


def endpoint_django(host: str="localhost", port: int=27017):
    """A decorator for creating a Django endpoint that interacts with a Retriever instance.

    Args:
        host (str): The hostname or IP address of the MongoDB instance. Defaults to "localhost".
        port (int): The port number of the MongoDB instance. Defaults to 27017.

    Returns:
        function: The decorated function.
    """
    def decorator(func):
        """The decorator function.

        Args:
            func (function): The function to decorate.

        Returns:
            function: The decorated function.
        """
        data_retriever = Retriever(host,port)
        def wrapper(request,**kwargs):
            """The wrapper function.

            Args:
                request (Request): The Django request object.
                **kwargs: Additional keyword arguments.

            Returns:
                Response: The response from the decorated function.
            """
            try:
                query = json.loads(request.data)
                kwargs['key'] = query['key']
                kwargs['results'] = getattr(data_retriever,query['command'])(query)  
            except Exception as e:
                kwargs['error'] = f"endpoint error - {str(e)}. Retriever method {query['command']} error"
            return func(request, **kwargs)
        return wrapper
    return decorator



def endpoint_fastapi(request_def,host: str="localhost", port: int=27017):
    """
    A decorator for creating a FastAPI endpoint that interacts with a Retriever instance.

    Args:
        request_def (type): The type of the FastAPI request object.
        host (str): The hostname or IP address of the MongoDB instance. Defaults to "localhost".
        port (int): The port number of the MongoDB instance. Defaults to 27017.

    Returns:
        function: The decorated function.
    """
    def decorator(func):
        """The decorator function.

        Args:
            func (function): The function to decorate.

        Returns:
            function: The decorated function.
        """
        data_retriever = Retriever(host,port)
        def wrapper(request:request_def, response=None):
            """The wrapper function.

            Args:
                request (request_def): The FastAPI request object.
                response (dict): The response dictionary. Defaults to None.

            Returns:
                Response: The response from the decorated function.
            """   
            try:
                response= dict()
                query = json.loads(async_to_sync(request.json)())
                response['key'] = query['key']
                response['results'] = getattr(data_retriever,query['command'])(query)
            except Exception as e:
                response['error'] = f"endpoint error - {str(e)}. Retriever method {query['command']} error"
            return func(request, response)
        return wrapper
    return decorator




def endpoint_flask(request, host: str="localhost", port: int=27017):
    """A decorator for creating a Flask endpoint that interacts with a Retriever instance.

    Args:
        request (Request): The Flask request object.
        host (str): The hostname or IP address of the MongoDB instance. Defaults to "localhost".
        port (int): The port number of the MongoDB instance. Defaults to 27017.

    Returns:
        function: The decorated function.
    """
    def decorator(func):
        """The decorator function.

        Args:
            func (function): The function to decorate.

        Returns:
            function: The decorated function.
        """
        data_retriever = Retriever(host,port)
        def wrapper(results = None):   
            """The wrapper function.

            Args:
                results (dict): The results dictionary. Defaults to None.

            Returns:
                Response: The response from the decorated function.
            """
            try:
                results = dict()
                query = json.loads(request.get_json())
                results['key'] = query['key']
                results['results'] = getattr(data_retriever,query['command'])(query)
            except Exception as e:
                results['error'] = f"endpoint error - {str(e)}. Retriever method {query['command']} error"
            return func(results)
        return wrapper
    return decorator