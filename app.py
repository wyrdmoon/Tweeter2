import mariadb
from flask import Flask, request, Response
import json
import dbcreds
import random
import string 
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/api/user', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def user():
    if request.method == 'GET':
        conn = None
        cursor = None
        user = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user")
            user = cursor.fetchall()
        except Exception as error:
            print("Something went wrong : ")
            print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(user != None):
                return Response(json.dumps(user, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    
      
    elif request.method == 'POST':
        conn = None
        cursor = None
        username = request.json.get("username")
        bio = request.json.get("bio")
        birthdate = request.json.get("birthdate")
        email = request.json.get("email")
        rows = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user(username, bio, birthdate, email) VALUES (?,?,?,?)", [username,bio, birthdate, email])
            conn.commit()
            rows = cursor.rowcount
        except Exception as error:
            print("Something went wrong (THIS IS LAZY): ")
            print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                return Response("bio Posted", mimetype="text/html", status=201)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    
     
    elif request.method == "PATCH":
        conn = None
        cursor = None 
        username = request.json.get("username") 
        bio = request.json.get("bio")
        birthdate = request.json.get("birthdate")
        email = request.json.get("email")
        id =request.json.get("id")
        rows = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            if username != "" and username != None:
                cursor.execute("UPDATE user SET username=? WHERE id=?", [username, id])
            if bio != "" and bio != None:
                cursor.execute("UPDATE user SET bio=? WHERE id=?", [bio, id])
           
            conn.commit() 
            rows = cursor.rowcount    
        except Exception as error:
            print("Something went wrong (This is LAZY)")  
            print(error)  
        finally: 
            if cursor != None:
                cursor.close() 
            if conn != None:
                conn.rollback()
                conn.close()
            if (rows == 1):
                return Response("Updated Success", mimetype="text/html", status=204)
            else:
                return Response("Update Failed", mimetype="text/html", status=500)
    
    elif request.method == "DELETE":
        conn = None
        cursor = None 
        username = request.json.get("username") 
        bio = request.json.get("bio")
        birthdate = request.json.get("birthdate")
        email = request.json.get("email")
        id =request.json.get("id")
        rows = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user WHERE id=?", [id, username, bio, birthdate, email])
            conn.commit() 
            rows = cursor.rowcount    
        except Exception as error:
            print("Something went wrong (This is LAZY)")  
            print(error)  
        finally: 
            if cursor != None:
                cursor.close() 
            if conn != None:
                conn.rollback()
                conn.close()
            if (rows == 1):
                return Response("Delete Success", mimetype="text/html", status=204)
            else:
                return Response("Delete Failed", mimetype="text/html", status=500)     
    ###################################################################################
@app.route('/api/login', methods=['POST', 'DELETE'])
def user_session():
        
    if request.method == 'POST':
        conn = None
        cursor = None
        email = request.json.get("email")
        password = request.json.get("password")
        
        rows = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute ("SELECT id, email, password FROM user WHERE email = ? AND password = ? ", [email, password])
            
            user = cursor.fetchall()
            print(user)
            if len (user) == 1:
             
             cursor.execute ("INSERT INTO user_session (user_id, login_token) VALUES (?,?)", [user[0][0], random.random()]) 
             
             conn.commit()
             rows = cursor.rowcount 
            if(cursor.rowcount == 1):
                print("Login successful")
            else:
                print("Error")        
            #generate a logintoken and insert to user session table
        except Exception as error:
            print("Something went wrong (THIS IS LAZY): ")
            print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                return Response("Logged In", mimetype="text/html", status=201)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        login_token = request.json.get("get")
        
        rows = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("DELETE login_token FROM user_session WHERE login_token = (?)", [user, login_token])
            conn.commit() 
            rows = cursor.rowcount    
        except Exception as error:
            print("Something went wrong (This is LAZY)")  
            print("error")  
        finally: 
            if cursor != None:
                cursor.close() 
            if conn != None:
                conn.rollback()
                conn.close()
            if (rows == 1):
                return Response("Delete Success", mimetype="text/html", status=204)
            else:
                return Response("Delete Failed", mimetype="text/html", status=500)     
            
    