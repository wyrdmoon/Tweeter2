import mariadb
from flask import Flask, request, Response
import json
import dbcreds
import random
import string 
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

#######################################users######################################################################
@app.route('/api/user', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def user_endpoint():
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
    #######################user session############################################################
@app.route('/api/login', methods=['POST', 'DELETE'])
def user_session_endpoint():
        
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
        login_token = request.json.get("login_token")
        rows = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_session WHERE login_token = (?)", [login_token])
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
                return Response("Logout Success", mimetype="text/html", status=204)
            else:
                return Response("Logout Failed", mimetype="text/html", status=500)

###########################################follows######################################################
@app.route('/api/follows', methods=['GET', 'POST', 'DELETE'])
def follows_endpoint():
    if request.method == 'GET':
        conn = None
        cursor = None
        users = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT u.id, u.username, u.email, u.bio, u.birthdate FROM user_follows uf INNER JOIN user u ON u.id = uf.user_id")
            users = cursor.fetchall()
        except Exception as error:
            print("Something went wrong : ")
            print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(users != None):
                return Response(json.dumps(users, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)

     
    elif request.method == 'POST':
        conn = None
        cursor = None
        login_token = request.json.get("login_token")
        follow_id = request.json.get("follow_id")
        rows = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE login_token = ?", [login_token])
            user_id= cursor.fetchone()[0]
            cursor.execute("INSERT INTO user_follows (follow_id, user_id )VALUES(?,?)", [follow_id, user_id])
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
                return Response("You followed", mimetype="text/html", status=201)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        login_token = request.json.get("login_token")
        follow_id = request.json.get("follow_id")
        rows = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE login_token = ?", [login_token])
        
            user_id= cursor.fetchone()[0]
            print(user_id)
            print(follow_id)
            cursor.execute("DELETE FROM user_follows WHERE user_id = ? AND follow_id =? ", [user_id, follow_id])
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
                return Response("unfollow success", mimetype="text/html", status=204)
            else:
                return Response("unfollow Failed", mimetype="text/html", status=500)   
    
########################################followers################################################################## 
@app.route('/api/followers', methods=['GET'])
def followers_endpoint():
    if request.method == 'GET':
        conn = None
        cursor = None
        user = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT follow_id FROM user_follows")
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
            
###########################################tweets###################################################################    
@app.route('/api/tweet', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def tweet_endpoint():
    if request.method == 'GET':
        conn = None
        cursor = None
        user = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tweet")
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
        login_token = request.json.get("login_token")
        content = request.json.get("content")
        rows = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM tweet",)
            user_id= cursor.fetchone()[0]
            cursor.execute("INSERT INTO tweet(user_id, content)VALUES(?,?)", [user_id, content])
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
                return Response("tweet Posted", mimetype="text/html", status=201)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
            
    
    elif request.method == "PATCH":
        conn = None
        cursor = None
        tweet_id = request.json.get("tweet_id")
        content = request.json.get("content")
        rows = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            if user_id != "" and user_id != None:
                cursor.execute("UPDATE user_id SET tweet_id=? WHERE login_token=?", [user_id, tweet_id])
            if bio != "" and bio != None:
                cursor.execute("UPDATE tweet_id SET content=? WHERE id=?", [content, tweet_id])
           
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
        login_token = request.json.get("login_token") 
        tweet_id = request.json.get("tweet_id")
        rows = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE login_token = ?", [login_token])
        
            user_id= cursor.fetchone()[0]
            cursor.execute("DELETE FROM tweet WHERE id = ? AND user_id = ? ",[tweet_id, user_id])
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

#######################################tweet-likes##################################################################
@app.route('/api/tweet_like', methods=['GET', 'POST', 'DELETE'])
def tweet_like_endpoint():
    if request.method == 'GET':
        conn = None
        cursor = None
        users = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT tweet_id FROM tweet_like")
            users = cursor.fetchall()
        except Exception as error:
            print("Something went wrong : ")
            print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(users != None):
                return Response(json.dumps(users, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
            
    
    elif request.method == 'POST':
        conn = None
        cursor = None
        login_token = request.json.get("login_token")
        tweet_id = request.json.get("tweet_id")
        rows = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE login_token = ?", [login_token])
            user_id= cursor.fetchone()[0]
            cursor.execute("INSERT INTO tweet_like (tweet_id, user_id)VALUES(?,?)", [tweet_id, user_id])
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
                return Response("You liked", mimetype="text/html", status=201)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
            
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        login_token = request.json.get("login_token")
        tweet_id = request.json.get("tweet_id")
        rows = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE login_token = ?", [login_token])
        
            user_id= cursor.fetchone()[0]
            print(user_id)
            print(tweet_id)
            cursor.execute("DELETE FROM tweet_like WHERE user_id = ? AND tweet_id =? ", [user_id, tweet_id])
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
                return Response("unlike success", mimetype="text/html", status=204)
            else:
                return Response("unlike Failed", mimetype="text/html", status=500)
            
  #####################################comments#####################################################################             
@app.route('/api/comment', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def comments_endpoint():
    if request.method == 'GET':
        conn = None
        cursor = None
        user = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM comment")
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
        
        tweet_id = request.json.get("tweet_id")
       
       
        content = request.json.get("content")
        login_token = request.json.get("login_token")
        
        rows = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE login_token =?", [login_token])
            user_id= cursor.fetchone()[0]
            cursor.execute("INSERT INTO comment(user_id, tweet_id, content)VALUES(?,?,?)", [user_id, tweet_id, content])
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
                return Response("comment Posted", mimetype="text/html", status=201)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
            
    elif request.method == "PATCH":
        conn = None
        cursor = None
        comment_id = request.json.get("comment_id")
        tweet_id = request.json.get("tweet_id")
        user_id = request.json.get("user_id")
        username = request.json.get("username")
        content = request.json.get("content")
        created_at = request.json.get("created_at")
        rows = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            if user_id != "" and user_id != None:
                cursor.execute("UPDATE user_id SET content=? WHERE login_token=?", [user_id, tweet_id])
            if content != "" and content != None:
                cursor.execute("UPDATE comment SET content=? WHERE id=?", [content, tweet_id])
           
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
        login_token = request.json.get("login_token") 
        comment_id = request.json.get("commentId")
        rows = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE login_token= ?", [login_token])
            user_id= cursor.fetchone()[0]
            cursor.execute("DELETE FROM comment WHERE user_id= ? AND id = ?", [user_id, comment_id])
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

    