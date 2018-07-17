# Item Catalog PROJECT

This project was set up using Python, HTML, CSS, Bootstrap, Flask, SQLAlchemy, OAuth2.0 

Item Catalog Web Applicatioin provides multiple categories and items under particular categories where users can login to create, edit, delete items. It utilizes RESTful Apis and essentially aloows users to perform CRUD. For authentication uses Google OAuth and authorization has also been implemented as well. 

## Getting Started

Make sure you have Python 2.7 installed onto your machine. Vagrant/VirtualBox is recommended.

### Prerequisites

Install pycodestyle to test code style

```
pip install pycodestyle
```

Make sure to set up the environment nessessary to run the application like Python, sign up for Google Account to receive clientid and secrets, etc.

### How to run

Run the following command onto terminal:

```
python application.py
```

Server will be running!

### And coding style tests

To check Python style: 

```
pycodestyle application.py
```

## Setting Up Environment

1. Clone this repo
2. Run
```
python database_setup.py
```
To initialize and create DB locally
3. Run 
```
python seed_data.py
```
This is will seed dummy data into database
3. Run
```
python application.py
```
4. Once running, goto http://localhost:3000/
and explore

## REST API Endpoints

1. / or /catalog - to access main page
2. /catalog/category_name - to access categories and items that falls under
3. /catalog/category_name/item - to access item name and description
4. /catalog.json - returns JSON file of all items and categories
5. /login - to login to google
6. ... there are many more endpoints to explore! Navigate!


## Improvements for Future

Need to work on front-end, styling, and better UI design.
Implment Facebook login and user registration.
Add in validation features for the forms.

## Authors

John C