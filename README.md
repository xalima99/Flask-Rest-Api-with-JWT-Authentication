# Flask-Rest-Api-with-JWT-Authentication
A simple Todo Flask RESTful Api shipped with JWT auth. Made in my FLask learning process. Mane refactors will be operated in near future.


# USAGE
**first create and activate an virtualenv** 

    virtualenv venv --python=pyhton3
	

    source venv/bin/activate

run `pip instal -r requirements.txt`

***You are good to go :)***

    python3 app.py

*NB : By default, the local port will be 5000*

**User Endpoints:**
*/signup:* register endpoint
*/auth*: login endpoint, will give back JWT token if loggin success, and you must
add that token in your request header like the following : `JWT {YOUR TOKEN}`

**Todo Endpoints (only accessible if logged in) :**
*/todos :* retrieves all todos created by logged in user
*/todo* - method POST : Creates a new todo
*/todo/<string:id>:*
method GET : get a specific todo
method PUT : update a existing todo or creates a new one.
method DELETE: Deletes a Todo
