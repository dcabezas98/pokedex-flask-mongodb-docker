# flask-mongodb-docker

The original Pokedex in a dockerized Flask app with Flask and MongoDB in separate containers.

The web app includes a database with the usual operations (search, add, edit, delete) and some charts with statistics. It also has a REST API (two actually, one programmed with the *flask_restful* package and another programmed traditionally) that can be tested with the Postman collections found in the repository.
Other functionality (user sessions, maps, ...) has been integrated with the only pourpose of learning about the specific tools for them.

![pokedex](https://user-images.githubusercontent.com/24246102/234062059-e1b8b4a8-563c-4a28-b625-3e65ea943708.png)

### How to set it up on Ubuntu

The instructions are very simple and also work in many other Linux distributions. *You need **docker** and **docker-compose**, though.*

Just clone or download the repository and run `docker-compose build` and `docker-compose up` in your terminal.
Access the direction `http://0.0.0.0:5000/pokemon` in your web browser to access the app, but the pokedex will be empty.
To recover the database you may restore it from the shell, just run the following commands in another terminal:
```
docker exec -it name sh
mongorestore --drop
mongosh
```
The last line just opens the mongo shell, where you may interact with the database.

Hope you enjoy!
