# Todoapi
This is a Todo api created using FastAPI and PostgresSQL
It uses 0auth for its authorization and jwt token for authentication
A user has to be logged in to create, get, edit and delete todos with different methods (using todo id, name, and completed todo)
The user will be created using the signup route
all routes can be viewed using the FASTAPI swagger UI
User's data are protected and secured as there is a verification process for only the logged in user details to be shown, displayed and a user can act only on his own todo 
