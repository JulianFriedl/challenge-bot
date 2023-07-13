# Running the Bot

First connect to the Vm on Google Cloud Platform using ssh. Then with nohup, you can run something like this:

```bash
nohup python3 bot_app.py &
```

This will run the script in the background and redirect its output to a file called nohup.out. You can then close your SSH session and your script will keep running. To stop your script, you can use the kill command with the process ID of your script.The kill command is a command that sends a signal to a process to terminate it. The syntax of the kill command is:

```bash
kill [options] pid
```

Where pid is the process ID of the process you want to terminate. You can use different options to specify the type of signal you want to send, such as -SIGTERM, -SIGKILL, or -SIGINT. The default signal is -SIGTERM, which asks the process to terminate gracefully. If the process does not respond to -SIGTERM, you can use -SIGKILL, which forces the process to terminate immediately. You can also use -SIGINT, which simulates a keyboard interrupt (Ctrl+C) to the process.

For example, if you want to terminate your Python script with the process ID 1234, you can run:

```bash
kill 1234
```

This will send a -SIGTERM signal to your script and ask it to terminate. If your script does not terminate, you can run:

```bash
kill -SIGKILL 1234
```

This will send a -SIGKILL signal to your script and force it to terminate.

You can find the process ID by using the ps command with a filter, such as:

```bash
ps -ef | grep bot_app.py
```
