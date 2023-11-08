# Capstone Project
This is the capstone project for Udacity's full stack web developer course.

## Getting Started
### Prerequisits and Installation
* SQLAlchemy and Flask are used for the backend
* Python 3.9.x is used
* Auth0 and JWTs are used for authentication and role-based access control

## API References

### Getting Started
* Based URL: This app can be run locally or accessed through Render at ------
* Authentication: JWTs, roles, and permissions are handled via Auth0

### Error Handling
Errors are returned as JSON objects with the following formats:
```
{
    "success": False,
    "error": <status code>,
    "message": <error message>
}
```
The API will return 6 error types when requests fail:
* 400: bad request
    * this could also happen if permissions are not included in the payload
* 401: a variety of authorization errors
    * authorization header expected
    * autherization of type Bearer expected
    * bearer token expected
    * authorization malformed
    * token expired
    * incorrect claims
* 403: incorrect permissions
* 404: resource not found
* 405: method not allowed
* 422: cannot process
* 500: internal server error