# database querys
# gebruiken met database.functie

from CS50 import SQL
db = SQL("sqlite:///test.db")

# user in db
def user_in_db(username):
    data = db.execute("SELECT * FROM users WHERE username=:username", username=username)
    return data