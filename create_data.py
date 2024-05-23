#!/usr/bin/env python3

import json
from hashlib import sha3_512, md5
from mysql.connector import connect, Error
from colorama import Fore, Back

database = "pclub_secy_task"
NEWLINE = '\n'

with open("db_user.json", 'r') as file:
    login_details = json.load(file)
with open("blogs.json", 'r') as file:
    blogs = json.load(file)
with open("users.json") as file:
    users = json.load(file)

def createUser(user, password):
    return f'("{user}", "{sha3_512(user.encode()).hexdigest()}", "{md5(password.encode()).hexdigest()}"),'

def createBlog(index, blog):
    return f'({index}, "{blog["title"]}", "{blog["content"]}", "{blog["link"]}")'

if __name__ == "__main__":
    try:
        with connect(
            host="localhost",
            user=login_details["user"],
            password=login_details["password"],
        ) as connection:
            print("Connected to MySQL Successfully!")
            with connection.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE {database}")
                print(f"Created Database {Fore.GREEN}{database}{Fore.RESET}")
                cursor.execute(f"USE {database}")
                cursor.execute("""CREATE TABLE USERS(
                               user VARCHAR(20) PRIMARY KEY,
                               userhash VARCHAR(128),
                               password VARCHAR(32)
                )""")
                print(f"Created Table {Fore.CYAN}USERS{Fore.RESET}")
                cursor.execute(f"""INSERT INTO USERS (user, userhash, password) VALUES
{NEWLINE.join([createUser(user, password) for user, password in users.items()])}
("kaptaan", "{sha3_512('kaptaan'.encode()).hexdigest()}", "{md5('0123456789'.encode()).hexdigest()}")
                """)
                print(f"Inserted  Data of {Fore.BLUE}{len(users)}{Fore.RESET} Users")
                cursor.execute("""CREATE TABLE BLOGS(
                               id INT PRIMARY KEY,
                               title VARCHAR(100),
                               content VARCHAR(1000),
                               link VARCHAR(100)
                )""")
                print(f"Created Table {Fore.CYAN}BLOGS{Fore.RESET}")
                cursor.execute(f"""INSERT INTO BLOGS (id, title, content, link) VALUES
                                {(NEWLINE+',').join([createBlog(index, blog) for index, blog in enumerate(blogs)])}
                """)
                print(f"Inserted  Data of {Fore.BLUE}{len(blogs)}{Fore.RESET} Blogs")
                cursor.execute("""CREATE TABLE HINTS(
                               hint VARCHAR(150)
                )""")
                cursor.execute("""INSERT INTO HINTS (hint) VALUES
                                ("In the Users Table userhash is the hash of the username and the password is md5 hash."),
                                ("To Give a Physical Significance of their Weakness, if they were your window glass, they could be easily broken with a rock.")
                               """)
                print(f"Inserted {Fore.BLUE}2{Fore.RESET} {Back.YELLOW}{Fore.RED}Hints{Fore.RESET}{Back.RESET}")
                connection.commit()
    except Error as err:
        print(err)
