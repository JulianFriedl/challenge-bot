# Caching and Hashing in api_error_handling.py

The module contains api_error_handling.py a function for making API requests and handling HTTP errors.

## Caching

Caching is a technique of storing the results of previous requests in a local file system, so that they can be reused later without making another request to the same URL. This can improve the performance and efficiency of the program, as well as reduce the load on the API server.

The function `api_request` uses caching by creating a hash of the URL, headers and parameters of the request, and using it as the name of the cache file. The hash ensures that each request has a unique identifier, and avoids collisions or overwriting of different requests. The function checks if the cache file exists before making the request, and if it does, it loads the cached response from the file and returns it. Otherwise, it makes the request to the API server, and saves the response in the cache file for future use.

The cache files are stored in a directory named `./cache`, which is created if it does not exist. The function uses the `pickle` module to serialize and deserialize the JSON responses to and from binary files.

## Pickle
The pickle module is used  to save and load the JSON responses from the API requests. `pickle.dump()` is used to write the JSON response to the cache file, and `pickle.load()` to read it back. This way, you can store and retrieve complex Python objects such as dictionaries in a binary format.

## Hashing

Hashing is a process of transforming any data into a fixed-length string of characters, called a hash or a digest, that uniquely represents the original data. Hashing is useful for comparing or identifying data, as well as for generating unique identifiers or keys.

The function `api_request` uses hashing by importing the `hashlib` module and creating a SHA-256 hash object. The SHA-256 algorithm is a secure and widely used hashing algorithm that produces a 256-bit (32-byte) hash. The function updates the hash object with the URL, headers and parameters of the request, encoded as UTF-8 bytes. Then, it calls the `hexdigest` method to get the hexadecimal representation of the hash as a string. This string is used as the name of the cache file for that request.
