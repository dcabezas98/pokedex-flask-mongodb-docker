from pickleshare import *

db=PickleShareDB('usersDB')

def checkUser(user):
    return user in db

def getUser(user):
    if checkUser(user):
        return db[user]
    return None

def addUser(user,data):
    if not checkUser(user):
        db[user]=data

def delUser(user):
    del db[user]

