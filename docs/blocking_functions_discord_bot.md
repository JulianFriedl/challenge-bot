# Discord_Api
This Document describes how I dealt with blocking functions in my discord bot.

## Handling Blocking Functions

To avoid blocking the gateway task, you'll need to run your blocking functions in a non-blocking way. Blocking functions are those that take a long time to execute, such as requests, database queries, or complex calculations. If you run them synchronously, they will prevent your bot from sending and receiving heartbeats, which are pings used to let Discord know that your bot is still alive and connected. This can cause your bot to disconnect and lose functionality.

There are two main ways to run blocking functions in a non-blocking way: using `asyncio` or threading. `asyncio` is a Python module that provides a framework for writing asynchronous code using coroutines and tasks. Threading is a Python module that allows you to create and manage multiple threads of execution.

## Asynchronous Programming and `asyncio` in Python

### Introduction

Asynchronous programming allows certain parts of your code to yield control, permitting other tasks to run in the interim. Python’s `asyncio` library is a comprehensive solution for crafting asynchronous applications.

### `asyncio` in Detail

#### Basic Concepts

- **Coroutines**: Functions that can pause their execution and yield to other routines, then resume from where they left off. Declared with `async def`.
  
- **Event Loop**: The orchestrator of asynchronous code. It schedules and runs tasks and coroutines.
  
- **Tasks**: A way to schedule multiple coroutines to run concurrently.

#### How I used `asyncio` 

Snippet from the code:
```python
@bot.tree.command(name="total", description="Returns all challenge members and the amount they have to pay.")
async def total_command(interaction: discord.Interaction):
    """Slash Command Implementation of the total_command"""
    await interaction.response.defer()
    loop = asyncio.get_event_loop()
    embed_result = await loop.run_in_executor(None, TotalCommand().get_yearly_payments)
    await interaction.followup.send(embed=embed_result)
```
In the Discord bot, I employed the `asyncio` library to prevent blocking operations from freezing the bot. Specifically, I used the `loop.run_in_executor` method. Here's a breakdown:

1. **Initialize the Event Loop**:  
   `loop = asyncio.get_event_loop()`

   This retrieves the current event loop or creates a new one.

2. **Run Blocking Functions**:  
   `result = await loop.run_in_executor(None, blocking_function)`

   This runs the blocking function (`blocking_function`) in a separate thread, ensuring the main event loop isn't blocked.

## Event Loop

### What is an Event Loop?

The event loop is a central component of `asyncio` and many other asynchronous programming frameworks. At a high level, it's responsible for scheduling and executing tasks, managing I/O operations, and handling events.

The name "event loop" is quite descriptive: the loop constantly checks for events (like incoming data or task completions) and responds to them as necessary. For instance, in the context of the Discord bot, an "event" could be a message from a user or a signal that a long-running task has completed.

### How does the Event Loop work?

1. **Task Scheduling**: When you declare a coroutine using the `async def` syntax, you're essentially creating a special kind of function. This function doesn't run immediately when called; instead, it returns a coroutine object. To actually run the coroutine, you need to schedule it on the event loop using methods like `asyncio.create_task()`. Once scheduled, the event loop will take care of executing it.

2. **Concurrency Through Cooperation**: The magic of `asyncio`'s concurrency model comes from the `await` keyword. When a coroutine encounters `await`, it's signaling to the event loop that it's okay to pause execution of the current coroutine and work on something else. Later, once the awaited operation is complete (e.g., data has been fetched from a network), the loop will resume the coroutine from where it left off.

3. **I/O Operations**: One of the primary use cases for asynchronous programming is handling I/O-bound operations efficiently. Traditional synchronous I/O operations would block the entire application until they complete. With `asyncio`, when a coroutine starts an I/O operation (like a Ib request), it will `await` the result, letting the event loop handle other tasks in the meantime.

### Event Loop's Role in the Discord Bot

For the Discord bot, the event loop continuously listens for events from the Discord API (e.g., user messages, reactions, and other interactions). When such an event happens, the loop checks which function (or "event handler") corresponds to that event and runs it.

## `run_in_executor`

`asyncio`'s event loop provides a method called `run_in_executor` that allows for the execution of traditional blocking functions in a way that doesn't block the entire event loop. Here's a more in-depth look:

### What does `run_in_executor` do?

`run_in_executor` allows you to run any blocking function (a function that's not a coroutine and doesn't have `await`) in a separate thread or process. This way, while the blocking function is running, the event loop can continue handling other tasks.

### How does it work?

1. **Executor Argument**: The first argument to `run_in_executor` is an executor. Executors are objects from the `concurrent.futures` module. There are two primary types:
    - `ThreadPoolExecutor`: Uses threads to execute functions. Suitable for I/O-bound tasks.
    - `ProcessPoolExecutor`: Uses processes to execute functions. Ideal for CPU-bound tasks.

    If you pass `None` as the executor, `asyncio` will use a default `ThreadPoolExecutor`.

2. **Function and Arguments**: After the executor, you provide the blocking function you want to run and any arguments it needs.

3. **Awaiting the Result**: Since `run_in_executor` effectively offloads a blocking function to another thread or process, you need to `await` it in a coroutine to get the result when it's done.

### `run_in_executor` in the Discord Bot

Given that certain methods in the Discord bot are blocking and might take a while to run, I use `run_in_executor` to execute these methods in a separate thread. This way, the bot remains responsive to other commands and interactions, even if one command takes a while to process.

For example:

```python
result = await loop.run_in_executor(None, blocking_function, arg1, arg2)
```

This runs `blocking_function` in a separate thread (because I used the default executor), allowing the bot to handle other events while `blocking_function` is processing.

### Why and How I Use Locking

In our application, multiple commands may attempt to read from or write to a shared JSON file concurrently. Without proper synchronization, this could lead to race conditions, where the outcome of operations depends on the non-deterministic timing of events, potentially causing data corruption or loss.

To prevent such race conditions and ensure data integrity, I employ locking mechanisms. Locking ensures that only one operation can access the shared resource (in this case, the JSON file) at a time, serializing access to critical sections of the code that modify the file.

#### Synchronous Locking with `threading.Lock`

For operations that are executed in a synchronous context or within executor threads (via `loop.run_in_executor`), I use `threading.Lock`. This standard lock from the `threading` module is suitable for managing access to shared resources in a multi-threaded environment, where blocking operations are performed outside the `asyncio` event loop.

Example usage:

```python
from threading import Lock

file_lock = Lock()

def save_credentials():
    with file_lock:
        # Perform file operations
```


### Conclusion

By integrating `asyncio` for asynchronous programming and employing both `threading.Lock` and `asyncio.Lock` for appropriate synchronization, our application achieves high concurrency and maintains data integrity across asynchronous operations. This approach allows our Discord bot to efficiently handle multiple commands and interactions concurrently, providing a robust and responsive user experience.

