# Caching and Hashing

This document provides an overview of the concepts of caching and hashing, and how they're being used in the discord bot.

## Caching

Caching is a technique used in computing to store the result of an expensive or I/O bound operation, such as a network request or a complex computation, so that if the same operation is needed again, it can be retrieved from the cache instead of being recomputed or refetched.

Caching is used to store the results of API requests. When the application makes an API request, it first checks if the result of this request is already in the cache. If it is, it retrieves and uses this result directly. If it's not, it goes ahead and makes the API request, then stores the result in the cache for future use.

This caching is implemented using the `functools.lru_cache` decorator from Python's standard library. This decorator automatically handles the details of creating and managing the cache. It uses a Least Recently Used (LRU) strategy, meaning that when the cache is full, it discards the least recently used items first.

Here's a code snippet from the code that uses `functools.lru_cache`:

```python
@lru_cache(maxsize=128)
def cached_api_request(url, headers=None, params=None):
    ...
```

## Hashing

Hashing is a technique used to map data of arbitrary size to fixed-size values. The values produced by a hash function, called hash codes, are used to index data in hash tables or databases, among other things.

Hashing isn't directly used, but it's used implicitly by the `functools.lru_cache` decorator. This decorator uses the arguments to the decorated function to form the key used in the underlying cache. Since Python's dictionaries use hashes of their keys for quick access to values, `functools.lru_cache` also needs to be able to hash its keys.

When you use complex objects (like dicts, lists, or custom classes) as arguments to a function decorated with `functools.lru_cache`, these need to be made hashable (able to be used as dictionary keys) since the built-in Python types for these are not hashable. The `frozenset` function is used to make the headers and params arguments hashable, like so:

```python
@lru_cache(maxsize=128)
def cached_api_request(url, headers=frozenset(), params=frozenset()):
    ...
```

Note that when the cached function is called, the `frozenset` function must also be used to convert the headers and params arguments to frozensets:

```python
response, error_embed = cached_api_request(url, frozenset(headers.items()), frozenset(params.items()))
```

This allows `functools.lru_cache` to correctly form a unique key for each unique combination of url, headers, and params, so that it can retrieve the correct cached result when needed.