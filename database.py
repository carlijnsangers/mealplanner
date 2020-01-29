# database querys

from helpers import get_IP
from cs50 import SQL

db = SQL("sqlite:///test.db")

# user in users
def user_in_db(username):
    data = db.execute("SELECT * FROM users WHERE username=:username", username=username)
    return data

# insert user in db
def insert_in_users(username, password):
    db.execute("INSERT INTO users (username, hash) VALUES (%s, %s)", (username, password))
    return

# img, title
def get_recipe(idr):
    data = db.execute("SELECT image, title FROM meal WHERE id = :idr LIMIT 1", idr=idr)
    return data

# get menu
def get_menu(user_id):
    data = db.execute("SELECT image, title, id FROM meal WHERE user_id=:user_id", user_id = user_id)
    return data

# Get diet
def get_diet(user_id):
    diet = db.execute("SELECT diet FROM preferences WHERE user_id=:user_id", user_id=user_id)
    if diet:
        return diet[0]['diet']
    else:
        return "no diet"

# Get intolerances
def get_intolerances(user_id):
    intolerances = db.execute("SELECT allergy FROM preferences WHERE user_id=:user_id", user_id=user_id)
    if intolerances:
        return intolerances[0]['allergy'].replace(",", ", ")
    else:
        return None


# update menu, meal=dict
def update_menu(meal, user_id):
    db.execute("INSERT INTO meal (id, title, image, user_id) VALUES (%s, %s, %s, %s)",
                            (meal["id"], meal["title"], meal["image"], user_id))
    return

# verwijder item van menu
def del_meal(idr, user_id):
    db.execute("DELETE FROM meal WHERE id = :idr AND user_id=:user_id LIMIT 1", idr=idr, user_id=user_id)
    return

# Verwijder het hele menu
def del_meal_plan(user_id):
    db.execute("DELETE FROM meal WHERE user_id=:user_id", user_id=user_id)

# check of user in db
def check(user_id, database):
    check = db.execute("SELECT * FROM :database WHERE user_id=:user_id LIMIT 1", user_id=user_id, database=database)
    return check

# IP naar id in meal
def ip_to_id(user_id):
    db.execute("UPDATE meal SET user_id=:user_id WHERE user_id=:IP", user_id=user_id, IP = get_IP())
    return

# get favorites by user
def get_favorites(user_id):
    favorites = db.execute("SELECT * FROM favorites WHERE user_id=:user_id", user_id=user_id)
    return favorites

# get favorite by idr and user
def get_fav_idr(user_id, idr):
    favorite = db.execute("SELECT * FROM favorites WHERE user_id=:user_id AND id=:idr", user_id=user_id, idr=idr)
    return favorite

# remove a favorite
def del_fav(user_id, idr):
    db.execute("DELETE FROM favorites WHERE user_id=:user_id AND id=:idr", user_id=user_id, idr=idr)
    return

# add a favorite
def add_fav(user_id, idr):
    data = db.execute("SELECT image, title FROM meal WHERE id=:idr LIMIT 1", idr=idr)
    db.execute("INSERT INTO favorites (user_id, idr, image, title) VALUES (:user_id, :idr, :image, :title)",
            user_id=user_id, idr=idr, image=data[0]["image"], title=data[0]['title'])
    return

# update prefences in db
def update_pref(user_id, allergy, diet):
    db.execute("UPDATE preferences SET allergy=:allergy, diet=:diet WHERE user_id=:user_id", user_id=user_id, allergy=allergy, diet=diet)
    return

# add preference to db
def add_pref(user_id, allergy, diet):
    db.execute("INSERT INTO preferences (user_id, allergy, diet) VALUES (:user_id, :allergy, :diet)",
            user_id=user_id, allergy=allergy, diet=diet)
    return
