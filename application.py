#!/usr/bin/python
from flask import (Flask,
                   render_template,
                   url_for,
                   jsonify,
                   flash,
                   make_response,
                   request,
                   redirect)
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Base, Category, CategoryItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
from functools import wraps

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog App"

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = scoped_session(DBSession)

# Main Homepage


@app.route('/')
@app.route('/catalog/')
def showCatalogs():
    """
    method/class name: Show available catalogs
    Args: NAN
    Returns: 
        return all catalogs available
    """
    categories = session.query(Category).order_by(asc(Category.name)).all()
    latest_items = (
        session.query(
            CategoryItem, Category
        )
        .join(Category, CategoryItem.cat_id == Category.id)
        .order_by(desc(CategoryItem.id)).all()
    )

    if 'username' not in login_session:
        return render_template('publicLatestItems.html',
                               categories=categories,
                               latest_items=latest_items)
    else:
        return render_template('latestItems.html',
                               categories=categories,
                               latest_items=latest_items)

# Read Catalogs and Items Under that Catalog


@app.route('/catalog/<path:catalog_name>/')
@app.route('/catalog/<path:catalog_name>/items')
def showCatalogItems(catalog_name):
    """
    method/class name: show items for one catalog
    Args:
        catalog_name: name of the catalog selected
    Returns:
        return all items under that catalog
    """
    categories = session.query(Category).order_by(asc(Category.name)).all()
    category_selected = session.query(
        Category).filter_by(name=catalog_name).one()
    category_items = session.query(
        CategoryItem).filter_by(cat_id=category_selected.id).all()
    category_count = session.query(
        CategoryItem).filter_by(cat_id=category_selected.id).count()

    return render_template('categoryItems.html',
                           categories=categories,
                           category_count=category_count,
                           category_name=catalog_name,
                           category_items=category_items)

# Read Item Description


@app.route('/catalog/<path:catalog_name>/<int:item_id>')
def itemDescription(catalog_name, item_id):
    item_description = session.query(
        CategoryItem).filter_by(id=item_id).one()
    if 'username' in login_session and item_description.user_id == login_session['user_id']:
        return render_template('itemDescription.html',
                               item_description=item_description)
    else:
        return render_template('publicItemDescription.html',
                               item_description=item_description)

# Read JSON


@app.route('/catalog.json')
def catalogJSON():
    """
    method/class name: All catalogs and items JSON
    Args: NAN
    Returns: JSON of all categories and items

    """
    all_categories_items = []
    categories = session.query(Category).all()
    for category in categories:
        items = session.query(CategoryItem).filter_by(cat_id=category.id).all()
        each_catalog = {}
        each_catalog["id"] = category.id
        each_catalog["name"] = category.name
        each_catalog["Item"] = [i.serialize for i in items]
        for each_item in each_catalog["Item"]:
            each_item["cat_id"] = category.id

        all_categories_items.append(each_catalog)
    return jsonify(Category=all_categories_items)


@app.route('/catalog/<path:catalog_name>/<int:item_id>/JSON')
def itemJSON(catalog_name, item_id):
    one_item = session.query(CategoryItem).filter_by(id=item_id).one()
    return jsonify(One_Item=one_item.serialize)


@app.route('/catalog/<path:catalog_name>/JSON')
def categoryJSON(catalog_name):
    category_selected = session.query(
        Category).filter_by(name=catalog_name).one()
    category_items = session.query(
        CategoryItem).filter_by(cat_id=category_selected.id).all()
    return jsonify(Catalog_Item=[i.serialize for i in category_items])


# Login Page


@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# Authentication Via Google


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    request.get_data()
    code = request.data.decode('utf-8')

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']

    # See if user exists, if not make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    flash("you are now logged in as %s" % login_session['username'])
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None

# Disconnect / Logout


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['user_id']
        del login_session['email']
        return ("<script>function myFunction()"
                "{alert('Successfully Disconnected');"
                "setTimeout(function () {window.location.href"
                "= '/catalog';}, 100);}</script>"
                "<body onload='myFunction()''>")
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

# Check user login status function decorator


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash("You are not authorized for access there")
            return redirect('/login')
    return decorated_function

# Add new item


@app.route('/catalog/new/', methods=['GET', 'POST'])
@login_required
def newItem():
    if request.method == 'POST':
        newItem = CategoryItem(title=request.form['title'],
                               description=request.form['description'],
                               cat_id=request.form['category'],
                               user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('New Item %s Successfully Created' % (newItem.title))
        return redirect(url_for('showCatalogs'))
    else:
        categories = session.query(Category).order_by(asc(Category.name)).all()
        return render_template('newItem.html',
                               categories=categories)

# Edit item


@app.route('/catalog/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def editItem(item_id):
    """
    method/class name: edit selected item
    Args:
        item_id: selected item's ID
    Returns:
        edit item in DB and return to main page
    """
    editedItem = session.query(CategoryItem).filter_by(id=item_id).one()

    if editedItem.user_id != login_session['user_id']:
        flash('You are not authorized to edit this item!')
        return redirect(url_for('showCatalogs'))
    if request.method == 'POST':
        if request.form['title']:
            editedItem.title = request.form['title']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category']:
            editedItem.cat_id = request.form['category']
        session.add(editedItem)
        session.commit()
        flash('Edited Item %s Successfully Created' % (editedItem.title))
        return redirect(url_for('showCatalogs'))
    else:
        categories = session.query(Category).order_by(asc(Category.name)).all()
        return render_template('editItem.html',
                               categories=categories)

# Delete item


@app.route('/catalog/<int:item_id>/delete', methods=['GET', 'POST'])
@login_required
def deleteItem(item_id):
    """
    method/class name: Delete selected item
    Args:
        item_id: id of the selected item
    Returns:
        redirect page, deleted item
    """
    deleteItem = session.query(
        CategoryItem).filter_by(id=item_id).one()

    if deleteItem.user_id != login_session['user_id']:
        flash('You are not authorized to delete this item!')
        return redirect(url_for('showCatalogs'))
    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()
        flash('Deleted Item %s' % item_id)
        return redirect(url_for('showCatalogs'))
    else:
        return render_template('deleteItem.html')


if __name__ == '__main__':
    app.secret_key = 'secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=3000)
