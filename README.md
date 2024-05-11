# ToggleFeature

## View all endpoints :
#### To run command on terminal -  $ python manage.py routes

### o/p - 
### Endpoint                        Methods  Rule
------------------------------  -------  ------------------------------------------
api_v1.create_user              POST     /api/v1/users
api_v1.get_user                 GET      /api/v1/users/<int:user_id>
api_v1.get_users                GET      /api/v1/users
static                          GET      /static/<path:filename>
toggle_blueprint.create_toggle  POST     /api/v1/toggles/<string:env>/<int:user_id>
toggle_blueprint.get_toggle     GET      /api/v1/toggles/<int:toggle_id>
toggle_blueprint.get_toggles    GET      /api/v1/toggles
toggle_blueprint.update_toggle  PUT      /api/v1/toggles/<int:toggle_id>


### - Create & Initialise Database 
#### : Run following commands

$ python manage.py db init
$ python manage.py db migrate
$ python manage.py db upgrade


- Start the Toggle Flask application
$ python manage.py run

#### output : 
 * Environment: development
 * Debug mode: on
 * Debugger is active!
 * Debugger PIN: 521-173-836
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

### Pytest 

#### Please refer app/tests/test_toggles.py

Pytest Result : 
-------------------------------------------------------------
test_toggles.py::test_get_toggles  PASSED                                
test_toggles.py::test_create_user  PASSED                                
test_toggles.py::test_get_user_detail_by_user_id  PASSED                  
test_toggles.py::test_get_user_detail_by__invalid_user_id  PASSED
test_toggles.py::test_create_user_with_invalid_role  PASSED
test_toggles.py::test_create_toggle  PASSED                               
test_toggles.py::test_create_duplicate_toggle_with_same_identifier  PASSED   
test_toggles.py::test_update_toggle  PASSED    






















