import pymongo
import os
from helper.date import add_date
from config import *
mongo = pymongo.MongoClient(DATABASE_URL)
db = mongo[DATABASE_NAME]
dbcol = db["user"]



# Total User
def total_user():
    user = dbcol.count_documents({})
    return user


# Insert Bot Data
def botdata(chat_id):
    bot_id = int(chat_id)
    try:
        bot_data = {"_id": bot_id, "total_rename": 0, "total_size": 0}
        dbcol.insert_one(bot_data)
    except:
        pass


# Total Renamed Files
def total_rename(chat_id, renamed_file):
    now = int(renamed_file) + 1
    dbcol.update_one({"_id": chat_id}, {"$set": {"total_rename": str(now)}})


# Total Renamed File Size
def total_size(chat_id, total_size, now_file_size):
    now = int(total_size) + now_file_size
    dbcol.update_one({"_id": chat_id}, {"$set": {"total_size": str(now)}})


# Insert User Data
def insert(chat_id):
    user_id = int(chat_id)
    user_det = {"_id": user_id, "file_id": None, "caption": None, "daily": 0, "date": 0,
                "uploadlimit": 5368709120, "used_limit": 0, "usertype": "Free", "prexdate": None,
                "metadata": False, "metadata_code": "By @Madflix_Bots",
                "intro": False, "intro_file": None, "outro": False, "outro_file": None, "watermark": False,
                "watermark_file": None, "watermark_position": "top-right", "text_watermark": None, "text_watermark_status": False}
    

    try:
        dbcol.insert_one(user_det)
    except:
        return True
        pass


# Add Thumbnail Data
def addthumb(chat_id, file_id):
    dbcol.update_one({"_id": chat_id}, {"$set": {"file_id": file_id}})

def delthumb(chat_id):
    dbcol.update_one({"_id": chat_id}, {"$set": {"file_id": None}})




# ============= Metadata Function Code =============== #

def setmeta(chat_id, bool_meta):
    dbcol.update_one({"_id": chat_id}, {"$set": {"metadata": bool_meta}})

def setmetacode(chat_id, metadata_code):
    dbcol.update_one({"_id": chat_id}, {"$set": {"metadata_code": metadata_code}})

# ============= Metadata Function Code =============== #



# Add Caption Data
def addcaption(chat_id, caption):
    dbcol.update_one({"_id": chat_id}, {"$set": {"caption": caption}})

def delcaption(chat_id):
    dbcol.update_one({"_id": chat_id}, {"$set": {"caption": None}})


# ================= VIDEO EDIT SETTINGS ================= #

def set_intro(chat_id, status):
    dbcol.update_one({"_id": chat_id}, {"$set": {"intro": status}})

def set_intro_file(chat_id, file_id):
    dbcol.update_one({"_id": chat_id}, {"$set": {"intro_file": file_id}})


def set_outro(chat_id, status):
    dbcol.update_one({"_id": chat_id}, {"$set": {"outro": status}})

def set_outro_file(chat_id, file_id):
    dbcol.update_one({"_id": chat_id}, {"$set": {"outro_file": file_id}})


def set_watermark(chat_id, status):
    dbcol.update_one({"_id": chat_id}, {"$set": {"watermark": status}})

def set_watermark_file(chat_id, file_id):
    dbcol.update_one({"_id": chat_id}, {"$set": {"watermark_file": file_id}})


def set_watermark_position(chat_id, position):
    dbcol.update_one({"_id": chat_id}, {"$set": {"watermark_position": position}})

def set_text_watermark(chat_id, text):
    dbcol.update_one({"_id": chat_id}, {"$set": {"text_watermark": text}})


def set_text_watermark_status(chat_id, status):
    dbcol.update_one({"_id": chat_id}, {"$set": {"text_watermark_status": status}})

def dateupdate(chat_id, date):
    dbcol.update_one({"_id": chat_id}, {"$set": {"date": date}})

def used_limit(chat_id, used):
    dbcol.update_one({"_id": chat_id}, {"$set": {"used_limit": used}})

def usertype(chat_id, type):
    dbcol.update_one({"_id": chat_id}, {"$set": {"usertype": type}})

def uploadlimit(chat_id, limit):
    dbcol.update_one({"_id": chat_id}, {"$set": {"uploadlimit": limit}})


# Add Premium Data
def addpre(chat_id):
    date = add_date()
    dbcol.update_one({"_id": chat_id}, {"$set": {"prexdate": date[0]}})

def addpredata(chat_id):
    dbcol.update_one({"_id": chat_id}, {"$set": {"prexdate": None}})

def daily(chat_id, date):
    dbcol.update_one({"_id": chat_id}, {"$set": {"daily": date}})

def find(chat_id):
    id = {"_id": chat_id}
    x = dbcol.find(id)
    for i in x:
        file = i["file_id"]
        try:
            caption = i["caption"]
        except:
            caption = None
        try:
            metadata = i["metadata"]
        except:
            metadata = False
        try:
            metadata_code = i["metadata_code"]
        except:
            metadata_code = None

        try:
            intro = i["intro"]
        except:
            intro = False

        try:
            intro_file = i["intro_file"]
        except:
            intro_file = None

        try:
            outro = i["outro"]
        except:
            outro = False

        try:
            outro_file = i["outro_file"]
        except:
            outro_file = None

        try:
            watermark = i["watermark"]
        except:
            watermark = False

        try:
            watermark_file = i["watermark_file"]
        except:
            watermark_file = None

        try:
            watermark_position = i["watermark_position"]
        except:
            watermark_position = "top-right"

        try:
            text_watermark = i["text_watermark"]
        except:
            text_watermark = None

        try:
            text_watermark_status = i["text_watermark_status"]
        except:
            text_watermark_status = False
            


        return [
            file,
            caption,
            metadata,
            metadata_code,
            intro,
            intro_file,
            outro,
            outro_file,
            watermark,
            watermark_file,
            watermark_position,
            text_watermark,
            text_watermark_status
       ]         

def getid():
    values = []
    for key in dbcol.find():
        id = key["_id"]
        values.append((id))
    return values

def delete(id):
    dbcol.delete_one(id)

def find_one(id):
    return dbcol.find_one({"_id": id})



    

# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Back-Up Channel @JishuBotz
# Developer @JishuDeveloper & @MadflixOfficials
