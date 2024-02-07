# Flask App Documentation

## Introduction

This Flask app (Version: 2.3.2) is designed to handle incoming requests at the `/strava_auth` endpoint. It is called when the user is redirected back to our application from the Strava authorization page after granting permission. It extracts the authorization code from the request and passes it to our Discord bot.

## Usage

To use the app, make a GET request to the `/strava_auth` endpoint with the `code` parameter set to the authorization code returned by Strava.

The app will return:

    Authorization successful! You can close this window.


## API Reference

### `/strava_auth`

Handles incoming requests at the `/strava_auth` endpoint.

This function is called when the user is redirected back to our application
from the Strava authorization page after granting permission. It extracts
the authorization code from the request and passes it to our Discord bot.

#### Request Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `code` | string | Yes | The authorization code returned by Strava. |

#### Response

If the authorization is successful, returns:

    Authorization successful! You can close this window.

---

## General Information

### What is a web server?

A web server is a computer program that serves content (such as HTML pages and images) over the internet.

### How does a web server work?

When a client (such as a web browser) sends a request to a web server, the server responds by sending back content (such as an HTML page). The client then renders this content and displays it to the user.

### What is Flask?

Flask is a micro web framework written in Python. It is classified as a microframework because it does not require particular tools or libraries. It has no database abstraction layer, form validation, or any other components where pre-existing third-party libraries provide common functions.

### How does Flask work?

Flask works by using decorators to mark Python functions as endpoints for handling HTTP requests sent by clients. These endpoints can return HTML pages, JSON data, or other types of content.

### Waitress (Version: 2.0.0)

Waitress is a pure Python WSGI server that can be used to serve Flask applications. It is easy to configure and supports Windows directly. It is easy to install as it does not require additional dependencies or compilation. However, it does not support streaming requests, and full request data is always buffered. It uses a single process with multiple thread workers.

### Http Protocol

The first line is the request line, which specifies the method, the path, and the HTTP version. The next lines are the header fields, which start with the name of the header, followed by a colon, a space, and the value of the header. The last line is an empty line, which indicates the end of the headers.

To send this message to the server, you need to use a tool that can establish a TCP connection and transmit data over it. One such tool is netcat, which is a command-line utility that can read and write data across network connections. To use netcat to send the message, you can save the message in a file (e.g., request.txt) and then use the following command:

`nc www.example.com 80 < request.txt`

The `nc` command invokes netcat, followed by the hostname and the port number of the server (80 is the default port for HTTP). The `<` symbol redirects the input from the file to netcat. Netcat will then send the message to the server and display the response on the terminal.

#### Example request

The activities endpoint in the strava API allows you to get data about your own or another athlete's activities, such as id, name, type, distance, start date, etc. You can also use parameters to filter and sort the results. Here is an example of a GET request to the activities endpoint that fetches the summary representation of the current athlete's activities:

```http
GET /api/v3/athlete/activities HTTP/1.1
Host: www.strava.com
Authorization: Bearer [access_token]
```

The code block above shows how to format the request as code. The first line specifies the method (GET), the path (/api/v3/athlete/activities), and the protocol version (HTTP/1.1). The second line specifies the host name (www.strava.com). The third line specifies the authorization header with the access token that identifies the athlete and the application making the call.

You can also add optional query parameters to the path, such as:

- `before`: An epoch timestamp to use for filtering activities that have taken place before a certain time.
- `after`: An epoch timestamp to use for filtering activities that have taken place after a certain time.
- `page`: Page number. Defaults to 1.
- `per_page`: Number of items per page. Defaults to 30.

For example, if you want to get the first 10 activities of the current athlete that have taken place after January 1st, 2023, you can use the following path:

```http
/api/v3/athlete/activities?after=1640995200&page=1&per_page=10
```

The response from the server will be in JSON format and will contain an array of summary representations of the activities.

#### Example Response 

The response might look something like this:

```
HTTP/1.1 200 OK
Date: Mon, 31 Jul 2023 10:44:38 GMT
Server: Strava
Content-Type: application/json; charset=utf-8
Content-Length: 1234

[
  {
    "id": 123456789,
    "name": "Morning Ride",
    "type": "Ride",
    "distance": 10000,
    "start_date_local": "2023-07-31T08:00:00Z",
    ...
  },
  {
    "id": 987654321,
    "name": "Evening Run",
    "type": "Run",
    "distance": 5000,
    "start_date_local": "2023-07-30T18:00:00Z",
    ...
  },
  ...
]
```

The first line is the status line, which shows the HTTP version, the status code, and the status message. The next lines are the header fields, which provide information about the server, the resource, or the connection. The last part is the body of the response, which contains the content of the resource (in this case, a JSON array of summary representations of the activities).

