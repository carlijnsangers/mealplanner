# database querys

from helpers import get_IP
from cs50 import SQL

db = SQL("sqlite:///mealplanner.db")

# checks if user in users
def user_in_db(username):
    data = db.execute("SELECT * FROM users WHERE username=:username", username=username)
    return data

# inserts user in db
def insert_in_users(username, password):
    db.execute("INSERT INTO users (username, hash) VALUES (%s, %s)", (username, password))
    return

# gets img, title by recipe id
def get_recipe(idr):
    data = db.execute("SELECT image, title FROM meal WHERE id = :idr LIMIT 1", idr=idr)
    return data

# gets menu of user
def get_menu(user_id):
    data = db.execute("SELECT image, title, id FROM meal WHERE user_id=:user_id", user_id = user_id)
    return data

# gets diet of user
def get_diet(user_id):
    diet = db.execute("SELECT diet FROM preferences WHERE user_id=:user_id", user_id=user_id)
    if diet:
        return diet[0]['diet']
    else:
        return "no diet"

# gets intolerances of user
def get_intolerances(user_id):
    intolerances = db.execute("SELECT allergy FROM preferences WHERE user_id=:user_id", user_id=user_id)
    if intolerances:
        return intolerances[0]['allergy'].replace(",", ", ")
    else:
        return None

# adds menu item
def update_menu(meal, user_id):
    db.execute("INSERT INTO meal (id, title, image, user_id) VALUES (%s, %s, %s, %s)",
                            (meal["id"], meal["title"], meal["image"], user_id))
    return

# removes item from menu/meal
def del_meal(idr, user_id):
    db.execute("DELETE FROM meal WHERE id = :idr AND user_id=:user_id LIMIT 1", idr=idr, user_id=user_id)
    return

# removes entire menu from meals
def del_meal_plan(user_id):
    db.execute("DELETE FROM meal WHERE user_id=:user_id", user_id=user_id)

# checks if user in a table
def check(user_id, database):
    check = db.execute("SELECT * FROM :database WHERE user_id=:user_id LIMIT 1", user_id=user_id, database=database)
    return check

# converts ip to id in table
def ip_to_id(user_id, database):
    db.execute("UPDATE :database SET user_id=:user_id WHERE user_id=:IP", user_id=user_id, IP = get_IP(), database=database)
    return

# get favorites by user
def get_favorites(user_id):
    favorites = db.execute("SELECT * FROM favorites WHERE user_id=:user_id", user_id=user_id)
    return favorites

# get favorite by idr and user
def get_fav_idr(user_id, idr):
    favorite = db.execute("SELECT * FROM favorites WHERE user_id=:user_id AND id=:idr", user_id=user_id, idr=idr)
    return favorite

# remove a favorite by user
def del_fav(user_id, idr):
    db.execute("DELETE FROM favorites WHERE user_id=:user_id AND id=:idr", user_id=user_id, idr=idr)
    return

# add a favorite by user
def add_fav(user_id, idr):
    data = db.execute("SELECT image, title FROM meal WHERE id=:idr LIMIT 1", idr=idr)
    db.execute("INSERT INTO favorites (user_id, id, image, title) VALUES (:user_id, :idr, :image, :title)",
            user_id=user_id, idr=idr, image=data[0]["image"], title=data[0]['title'])
    return

# updates prefences of user
def update_pref(user_id, allergy, diet):
    db.execute("UPDATE preferences SET allergy=:allergy, diet=:diet WHERE user_id=:user_id", user_id=user_id, allergy=allergy, diet=diet)
    return

# add preferences of user
def add_pref(user_id, allergy, diet):
    db.execute("INSERT INTO preferences (user_id, allergy, diet) VALUES (:user_id, :allergy, :diet)",
            user_id=user_id, allergy=allergy, diet=diet)
    return
