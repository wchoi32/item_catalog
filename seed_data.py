from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem, User

engine = create_engine('sqlite:///itemcatalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

session.query(Category).delete()
session.query(CategoryItem).delete()
session.query(User).delete()

user1 = User(name="john",
             email="test@test.com")
session.add(user1)
session.commit()

category1 = Category(name="Soccer", user=user1)
session.add(category1)
session.commit()

category2 = Category(name="Basketball", user=user1)
session.add(category2)
session.commit()

category3 = Category(name="Baseball", user=user1)
session.add(category3)
session.commit()

category4 = Category(name="Frisbee", user=user1)
session.add(category4)
session.commit()

category5 = Category(name="Snowboarding", user=user1)
session.add(category5)
session.commit()

category6 = Category(name="Rock Climbing", user=user1)
session.add(category6)
session.commit()

category7 = Category(name="Foosball", user=user1)
session.add(category7)
session.commit()

category8 = Category(name="Skating", user=user1)
session.add(category8)
session.commit()

category9 = Category(name="Hockey", user=user1)
session.add(category9)
session.commit()


categoryItem1 = CategoryItem(title="Soccer Cleats",
                             description="The shoes",
                             category=category1,
                             user=user1)
session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(title="Jersey",
                             description="the shirt",
                             category=category1,
                             user=user1)
session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(title="Orange Ball",
                             description="basketball",
                             category=category2,
                             user=user1)
session.add(categoryItem3)
session.commit()

categoryItem4 = CategoryItem(title="Jordan",
                             description="type of shoes",
                             category=category2,
                             user=user1)
session.add(categoryItem4)
session.commit()

categoryItem5 = CategoryItem(title="Stadium",
                             description="live stadium",
                             category=category2,
                             user=user1)
session.add(categoryItem5)
session.commit()

categoryItem6 = CategoryItem(title="Bat",
                             description="baseball bat",
                             category=category3,
                             user=user1)
session.add(categoryItem6)
session.commit()

categoryItem7 = CategoryItem(title="Baseball Cleets",
                             description="baseball shoes",
                             category=category3,
                             user=user1)
session.add(categoryItem7)
session.commit()

categoryItem8 = CategoryItem(title="glove",
                             description="baseball glove",
                             category=category3,
                             user=user1)
session.add(categoryItem8)
session.commit()

categoryItem9 = CategoryItem(title="base",
                             description="there are three bases, known as first, second, and thirdbase",
                             category=category3,
                             user=user1)
session.add(categoryItem9)
session.commit()


print("seeded all items!")
