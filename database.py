# database querys
# gebruiken met database.functie

from helpers import get_IP
from cs50 import SQL
db = SQL("sqlite:///test.db")

# user in db
def user_in_db(username):
    data = db.execute("SELECT * FROM users WHERE username=:username", username=username)
    return data

# img, title
def get_recipe(idr):
    data = db.execute("SELECT image, title FROM meal WHERE id = :idr LIMIT 1", idr=idr)
    return data

# get menu
def get_menu(user_id):
    data = db.execute("SELECT image, title, id FROM meal WHERE user_id=:user_id", user_id = user_id)
    return data

# update menu, meal=dict
def update_menu(meal, user_id):
    db.execute("INSERT INTO meal (id, title, image, user_id) VALUES (%s, %s, %s, %s)",
            (meal["id"], meal["title"], meal["image"], user_id))
    return

# verwijder item van menu
def del_meal(idr, user_id):
    db.execute("DELETE FROM meal WHERE id = :idr AND user_id=:user_id", idr=idr, user_id=user_id)
    return

# check of user in db
def check(user_id, db):
    check = db.execute("SELECT * FROM :db WHERE id=:user_id", user_id=user_id, db=db)
    return check

# IP naar id in meal
def ip_to_id(user_id):
    db.execute("UPDATE meal SET user_id=:user_id WHERE user_id=:IP", user_id=user_id, IP = get_IP())
    return
