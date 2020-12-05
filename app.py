import mariadb
from flask import Flask, request, Response
import json
import dbcreds
import random
import string
import secrets
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

#######################################users######################################################################
@app.route('/api/users', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def user_endpoint():
    if request.method == 'GET':
        userId = request.args.get("userId")
        
        conn = None
        cursor = None
        user = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            if userId != None:
                cursor.execute("SELECT * FROM user WHERE id =?",[userId])
            else:
                cursor.execute("SELECT * FROM user")
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
                empty_array = []
                for user in users:
                    empty_array.append ({"userId":user[0], "email":user[2], "username":user[1], "bio":user[3], "birthdate":user[4]})
                return Response(json.dumps(empty_array, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    
      
    elif request.method == 'POST':
        conn = None
        cursor = None
        rows = None
        user = None
        username = request.json.get("username")
        bio = request.json.get("bio")
        birthdate = request.json.get("birthdate")
        email = request.json.get("email")
        password = request.json.get("password")
        
        
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user(username, bio, birthdate, email, password) VALUES (?,?,?,?,?)", [username,bio, birthdate, email, password])
            conn.commit()
            userId = cursor.lastrowid
            loginToken=secrets.token_urlsafe(20)
            cursor.execute("INSERT INTO user_session (user_id, login_token) VALUES (?,?)", [userId, loginToken])
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
                user={
                    "userId": userId,
                    "email": email,
                    "username": username,
                    "bio": bio,
                    "birthdate": birthdate,
                    "loginToken": loginToken
                }
           
               
                return Response(json.dumps(user, default=str), mimetype="application/json", status=201)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    
     
    elif request.method == "PATCH":
        conn = None
        cursor = None 
        username = request.json.get("username") 
        bio = request.json.get("bio")
        birthdate = request.json.get("birthdate")
        email = request.json.get("email")
        password = request.json.get("password")
        loginToken =request.json.get("loginToken")
        rows = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE login_token = ?", [loginToken])
            
            
            user_id= cursor.fetchone()[0]
            print(user_id)
            if username != "" and username != None:
                cursor.execute("UPDATE user SET username=? WHERE id=?", [username, user_id])
            if bio != "" and bio != None:
                cursor.execute("UPDATE user SET bio=? WHERE id=?", [bio, user_id])
            if password != "" and password != None:
                cursor.execute("UPDATE user SET password=? WHERE id=?", [password, user_id])
            if email != "" and email != None:
                cursor.execute("UPDATE user SET email=? WHERE id=?", [email, user_id])
            if birthdate != "" and birthdate != None:
                cursor.execute("UPDATE user SET birthdate=? WHERE id=?", [birthdate, user_id])
           
            conn.commit() 
            rows = cursor.rowcount 
            cursor.execute("SELECT * FROM user WHERE id = ?", [user_id])
            user = cursor.fetchone()   
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
                print(user)
                user_u = {"userId":user[0], "email":user[2], "username":user[1], "bio":user[3], "birthdate":user[4]}
                return Response(json.dumps(user_u), mimetype="application/json", status=200)
            else:
                return Response("Update Failed", mimetype="text/html", status=500)
    
    elif request.method == "DELETE":
        conn = None
        cursor = None
        loginToken = request.json.get("loginToken")
        password = request.json.get("password")
        rows = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE login_token = ?", [loginToken])
        
            user_id= cursor.fetchone()[0]
            cursor.execute("DELETE FROM user WHERE id=? AND password= ?", [user_id, password])
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
            cursor.execute ("SELECT * FROM user WHERE email = ? AND password = ? ", [email, password])
            
            user = cursor.fetchall()
            loginToken=secrets.token_urlsafe(20)
            print(user)
            if len (user) == 1:
             
                cursor.execute ("INSERT INTO user_session (user_id, login_token) VALUES (?,?)", [user[0][0], loginToken]) 
                conn.commit()
                rows = cursor.rowcount 
           
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
                user={
                    "userId": user[0][0],
                    "email": email,
                    "username": user[0][1],
                    "bio": user[0][3],
                    "birthdate": user[0][4],
                    "loginToken": loginToken
                }
           
                return Response(json.dumps(user,default=str), mimetype="application/json", status=201)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        login_token = request.json.get("loginToken")
        rows = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_session WHERE login_token = ?", [login_token])
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
        userId = request.args.get()
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT u.id, u.username, u.email, u.bio, u.birthdate FROM user_follows uf INNER JOIN user u ON u.id = uf.userId =?,"[userId])
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
                empty_array = []
                for user in users:
                     empty_array.append ({"userId":user[0], "email":user[2], "username":user[1], "bio":user[3], "birthdate":user[4]})
                return Response(json.dumps(empty_array, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)

     
    elif request.method == 'POST':
        conn = None
        cursor = None
        login_token = request.json.get("loginToken")
        follow_id = request.json.get("followId")
        rows = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE login_token = ?", [login_token])
            user_id= cursor.fetchone()[0]
            print(user_id)
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
                return Response("You followed", mimetype="text/html", status=204)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
    
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        login_token = request.json.get("loginToken")
        follow_id = request.json.get("followId")
        rows = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE login_token = ?", [login_token])
            print(follow_id)
            user_id= cursor.fetchone()[0]
            
            print(user_id)
            
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
        userId = request.args.get("userId")
        conn = None
        cursor = None
        user = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            if userId != None:
                cursor.execute("SELECT u.id, u.username, u.email, u.bio, u.birthdate FROM user_follows uf INNER JOIN user u ON u.id = uf.user_id WHERE uf.follow_id = ?",[userId])
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
                empty_array = []
                for user in users:
                    empty_array.append ({"userId":user[0], "email":user[2], "username":user[1], "bio":user[3], "birthdate":user[4]})
                return Response(json.dumps(empty_array, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)    
            
###########################################tweets###################################################################    
@app.route('/api/tweet', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def tweet_endpoint():
    if request.method == 'GET':
        
        conn = None
        cursor = None
        tweets = None
        userId = request.args.get("userId")
      
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            if userId != None:
                cursor.execute("SELECT * FROM tweet INNER JOIN user ON user.id = tweet.user_id WHERE tweet.user_id = ?", [userId,])
            else:
                cursor.execute("SELECT * FROM tweet INNER JOIN user ON user.id = tweet.user_id ")
            tweets = cursor.fetchall()
        except Exception as error:
            print("Something went wrong : ")
            print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(tweets != None):
                empty_array = []
                for tweet in tweets:
                  #for loop and dictionary
                    empty_array.append ({"tweetId":tweet[0],"userId":tweet[2], "username":tweet[5], "content":tweet[1], "createdAt":tweet[3]}) 
                return Response(json.dumps(empty_array, default=str), mimetype="application/json", status=200)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)

  
    elif request.method == 'POST':
        conn = None
        cursor = None
        login_token = request.json.get("loginToken")
        content = request.json.get("content")
        rows = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
          
        
           
            cursor.execute("SELECT user_id FROM user_session WHERE login_token = ?", [login_token])
            user_id= cursor.fetchone()[0]
            cursor.execute("SELECT username FROM user WHERE id = ?", [user_id])
            username= cursor.fetchone()[0]
            cursor.execute("INSERT INTO tweet(user_id, content)VALUES (?,?)", [user_id, content])
            conn.commit()
            rows = cursor.rowcount
            tweetId = cursor.lastrowid
            cursor.execute ("SELECT created_at from tweet WHERE id =?", [tweetId])
            createdAt = cursor.fetchone()[0]
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
                tweet ={
                    "tweetId" : tweetId,
                    "userId" : user_id,
                    "username": username,
                    "content": content,
                    "createdAt": createdAt
                }
                return Response(json.dumps(tweet, default=str), mimetype="application/json", status=201)
            else:
                return Response("Something went wrong!", mimetype="text/html", status=500)
            
    
    elif request.method == "PATCH":
        conn = None
        cursor = None
        loginToken = request.json.get("loginToken")
        tweetId = request.json.get("tweetId")
        content = request.json.get("content")
        rows = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE login_token = ?", [loginToken])
        
            user_id= cursor.fetchone()[0]
            if user_id != "" and user_id != None:
                cursor.execute("UPDATE tweet SET content=? WHERE user_id = ? AND id =?", [content, user_id, tweetId,])
          
           
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
                user ={
                    "tweetId": tweetId,
                    "content": content
                }
                return Response(json.dumps(user, default=str), mimetype="application/json", status=200)
            else:
                return Response("Update Failed", mimetype="text/html", status=500)
            
    elif request.method == "DELETE":
        conn = None
        cursor = None 
        loginToken = request.json.get("loginToken") 
        tweetId = request.json.get("tweetId")
        rows = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE login_token = ?", [loginToken])
        
            user_id= cursor.fetchone()[0]
            cursor.execute("DELETE FROM tweet WHERE id = ? AND user_id = ? ",[tweetId, user_id])
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
        login_token = request.json.get("loginToken")
        tweet_id = request.json.get("tweetId")
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
            
 #################################comment-likes#################################################################
@app.route('/api/comment-likes', methods=['GET', 'POST', 'DELETE'])
def comment_like_endpoint():
    if request.method == 'GET':
        conn = None
        cursor = None
        users = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT comment_id FROM comment_like")
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
        loginToken = request.json.get("loginToken")
        commentId = request.json.get("commentId")
        print(commentId)
        rows = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE login_token = ?", [loginToken])
            user_id = cursor.fetchone()[0]
            print(user_id)
           
            cursor.execute("INSERT INTO comment_like (comment_id, user_id)VALUES(?,?)", [commentId, user_id])
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
                return Response("this is a test!", mimetype="text/html", status=500)
            
          
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        loginToken = request.json.get("loginToken")
        commentId = request.json.get("commentId")
        rows = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE login_token = ?", [loginToken])
        
            user_id= cursor.fetchone()[0]
            print(user_id)
            print(commentId)
            cursor.execute("DELETE FROM comment_like WHERE user_id = ? AND comment_id =? ", [user_id, commentId])
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
            
          
   
    
    