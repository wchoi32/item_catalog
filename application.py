from flask import Flask, render_template, request, redirect, url_for, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem

from flask import session as login_session
import random
import string

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/catalog/')
def show_catalogs():
    categories = session.query(Category).order_by(asc(Category.name))
    latest_items = session.query(CategoryItem, Category).join(
        Category, CategoryItem.cat_id == Category.id).order_by(desc(CategoryItem.id))

    return render_template('latestItems.html',
                           categories=categories,
                           latest_items=latest_items)


@app.route('/catalog/<path:catalog_name>/')
@app.route('/catalog/<path:catalog_name>/items')
def show_catalog_items(catalog_name):
    categories = session.query(Category).order_by(asc(Category.name))
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


@app.route('/catalog/<path:catalog_name>/<path:item_name>')
def item_description(catalog_name, item_name):
    item_description = session.query(
        CategoryItem).filter_by(title=item_name).one()
    return render_template('itemDescription.html',
                           item_description=item_description)


@app.route('/catalog.json')
def catalog_json():
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


@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=3000)
