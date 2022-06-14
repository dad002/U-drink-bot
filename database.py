import configt
import psycopg2

db_connection = psycopg2.connect(configt.DATABASE_URI, sslmode="require")
db_object = db_connection.cursor()

def insert_user(user_id, username, first_name, last_name, date):
	db_object.execute("INSERT INTO users(id, username, first_name, last_name, last_activity) VALUES (%s, %s, %s, %s, %s)", 
							(user_id, username, first_name, last_name, date))
	db_connection.commit()

def insert_party(user_id, cocktails, quantity, name, desc):
	db_object.execute("INSERT INTO party (user_id, cocktails, quantity, name, description) VALUES (%s,%s,%s,%s,%s)", 
					(user_id, cocktails, quantity, name, desc))
	db_connection.commit()

def update_party(count, name, user_id):
	db_object.execute("UPDATE party SET quantity = %s WHERE name = %s and user_id = %s", (count, name, user_id))
	db_connection.commit()

def update_activity(date, user_id):
	db_object.execute("UPDATE users SET last_activity = %s WHERE id = %s", (date, user_id))
	db_connection.commit()

def delete_party_by_name(user_id, party_for_delete):
	db_object.execute(f"DELETE FROM party WHERE user_id={user_id} and name='{party_for_delete}'")
	db_connection.commit()

def check_user(user_id):
	db_object.execute(f"SELECT id FROM users WHERE id = {user_id}")
	return db_object.fetchone()

def select_partys_by_user_and_master(user_id):
	db_object.execute(f"SELECT * FROM party WHERE user_id = {user_id} OR user_id = {-1}")
	return db_object.fetchall()

def select_partys_by_user(user_id):
	db_object.execute(f"SELECT * FROM party WHERE user_id = {user_id}")
	return db_object.fetchall()

def select_party_by_name_and_user(name, user_id):
	db_object.execute(f"SELECT * FROM party WHERE name='{name}' and (user_id = {user_id} or user_id={-1})")
	return db_object.fetchone()

def select_masters_partys(name):
	db_object.execute(f"SELECT * FROM party WHERE name='{name}' and user_id={-1}")
	return db_object.fetchall()