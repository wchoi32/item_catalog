
from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem

app = Flask(__name__)

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


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


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=3000)
