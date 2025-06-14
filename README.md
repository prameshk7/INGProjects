# INGProjects
Backend Interview Round Tasks for Skill Museum &amp; Research Centre (SMaRC) | ING Skill Academy
- Blog App (Task 1): A simple blog system for creating and viewing posts.
- Todo App (Task 2): A RESTful API for managing todo tasks.
- Profile App (Task 3): Manages user registration, login, password reset, and profile editing.


## How to run the blog app?
- Click "Go to Blog App" to navigate to http://127.0.0.1:8000/blog/
- Visit the page to see a list of posts
- Register and Login to create a new blog
- Edit or delete the blog created by you

## How to run the todo app?
This is built with DRF so navigation maybe bit tricky.
- Click "Go to Todo App" to navigate to http://127.0.0.1:8000/api/todos<br/>
   [You can view all the todos of the user in this url.]
- Click Extra Actions dropdown and select "Regsiter" to register a new user to activate a session.
- After registration, click Todo List or go to URL - http://127.0.0.1:8000/api/todos to add new todo.
- After adding todo, you can retreive a specific task using url - http://127.0.0.1:8000/api/todos/id/
- After adding todo, you can choose to edit or delete todos created by you using url - http://127.0.0.1:8000/api/todos/id/
- Click Extra Actions dropdown and select "Login" to login a registered user to activate a session.
#### [ A registered/loggedin user can only CRUD on their todos.]

## How to run the userprofile app?
- Click "Go to Profile App" to navigate to http://127.0.0.1:8000/userprofile/register
- Register a user, log in, reset password, and update the profile.

### The dependencies can be installed by pip install -r requirements.txt
<br/>
<br/>
