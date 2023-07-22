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

### Best Practices for Developing Flask Apps

1. Use a secret key to secure your app.
2. Don’t use Flask’s development server in production.
3. Configure logging properly.
4. Use Blueprints to organize your application.
5. Use an ORM (e.g. SQLAlchemy) to interact with your database.
6. Use a proper database migration tool (e.g. Alembic) to manage schema changes.
7. Test your code thoroughly.
8. Make sure you know how to scale your app.

### Waitress (Version: 2.0.0)

Waitress is a pure Python WSGI server that can be used to serve Flask applications. It is easy to configure and supports Windows directly. It is easy to install as it does not require additional dependencies or compilation. However, it does not support streaming requests, and full request data is always buffered. It uses a single process with multiple thread workers.
