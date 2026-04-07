from asgiref.sync import async_to_sync

class shard_method:
    """A class to handle shard method requests from different endpoints.

    Args:
        request: The request object from the endpoint.
        endpoint (str): The type of endpoint (django, flask, fastapi).

    Attributes:
        called_methods (dict): The called methods from the request.
    """
    def __init__(self,request, endpoint: str) -> None:
        """Initializes the ShardMethod object.

        Args:
            request: The request object from the endpoint.
            endpoint (str): The type of endpoint (django, flask, fastapi).
        """
        if endpoint == 'django':
            query = request.data
        elif endpoint == 'flask':
            query = request.get_json()
        elif endpoint == 'fastapi':
            query = async_to_sync(request.json)()
        self.called_methods = query['called_methods']

    def main(self) -> str | None:
        """Returns the main method if it exists in the called methods.

        Returns:
            method (str): The main method.
            None: If 'main_method' is not in called methods.
        """
        if 'main_method' in self.called_methods:
            main_method = self.called_methods['main_method']
            return main_method['method']
        else:
            return None
        
    def main_with_args(self) -> tuple | None:
        """Returns the main method with arguments if it exists in the called methods.

        Returns:
            tuple: A tuple containing the main method and its arguments.
            None: If 'main_method' is not in called methods.
        """

        if 'main_method' in self.called_methods:
            main_method = self.called_methods['main_method']
            return (main_method['method'],main_method['args'])
        else:
            return None
        
    def chain(self) -> list | None:
        """Returns a list of chain methods if they exist in the called methods.

        Returns:
            list: A list of chain methods.
            None: If 'chain_methods' is not in called methods.
        """
        if 'chain_methods' in self.called_methods:
            chain_methods = [i['method'] for i in self.called_methods['chain_methods']]
            return chain_methods
        else:
            return None

    def chain_with_args(self) -> list | None:
        """Returns a list of chain methods with arguments if they exist in the called methods.

        Returns:
            list: A list of tuples containing the chain methods and their arguments.
            None: If 'chain_methods' is not in called methods.
        """
        if 'chain_methods' in self.called_methods:
            chain_methods = [(i['method'],i['args']) for i in self.called_methods['chain_methods']]
            return chain_methods
        else:
            return None



