import sqlite3
import datetime
import sys
from pathlib import Path

def resource_path(filename):
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / filename
    return Path(__file__).parent / filename
db = resource_path("stickerdb.db")
selectedaccount=""

def sql(file, command, type):
    """
    Type: 1=update/change the db, 2: Select things, 3: Select as dicts
    """
    try:
        con = sqlite3.connect(file)
        if type==3:
            con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(command)
        value = None
        if type==2 or type==3:
            value = cur.fetchall()
            if type == 3:
                value = [dict(row) for row in value]
        if type==1:
            con.commit()
        con.close()
        return value
    except Exception as e:
        text=f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')} \n {str(e)} \n {file}, {command}, {type}"
        return text
    
def count(file, command):
    count = sql(file, command, 2)
    return len(count)

def createaccount(name):
    sql(db, f"INSERT INTO players VALUES ({count(db, 'SELECT * from players;')+1}, '{name}');", 1)

def showaccount():
    acc=sql(db, 'SELECT * from players;', 2)
    for e in acc:
        print(f"Id:{e[0]} | name:{e[1]}")


def deleteaccount(name):
    try:
        plrid = sql(db, f"SELECT playerid from players where LOWER(playername)=LOWER('{name}');", 2)[0][0]
    except IndexError as e:
        print(e)
        print("This account must exist !")
        return None
    sql(db, f"DELETE from inventory where plrid={plrid};", 1)
    sql(db, f"DELETE from players where LOWER(playername)=LOWER('{name}');", 1)

def addsticker(name, sticker, amount):
    try:
        assert count(db, f"Select * from players where LOWER(playername)=LOWER('{name}');")!=0, "This account does not exist."
        assert count(db, f"Select * from stickers where stickername LIKE '{sticker}%';")!=0, "This sticker does not exist."
        if count(db, f"Select * from stickers where stickername='{sticker}';")==0:
            stickerid=sql(db, f"select stickerid from stickers where stickername LIKE '{sticker}%';", 2)[0][0]
        else:
            stickerid=sql(db, f"select stickerid from stickers where stickername='{sticker}';", 2)[0][0]
        playerid=sql(db, f"SELECT playerid from players where LOWER(playername)=LOWER('{name}');", 2)[0][0]
        if count(db, f"Select * from inventory where plrid={playerid} and sticker={stickerid};"):
            oldamount=sql(db, f"Select quantity from inventory where plrid={playerid} and sticker={stickerid};",2)[0][0]
            sql(db, f"update inventory set quantity={oldamount+amount} where plrid={playerid} and sticker={stickerid};",1)
        else:
            sql(db, f"INSERT INTO inventory values ({playerid}, {stickerid}, {amount});",1)
        print(f"Sucessfully added x{amount} of {sql(db, f'Select stickername from stickers where stickerid={stickerid};', 2)[0][0]} !")
    except Exception as e:
        print(e)



def removesticker(name, sticker, amount):
    try:
        assert count(db, f"Select * from players where LOWER(playername)=LOWER('{name}');")!=0, "This account does not exist."
        assert count(db, f"Select * from stickers where stickername LIKE '{sticker}%';")!=0, "This sticker does not exist."
        assert count(db, f"Select * from players where LOWER(playername)=LOWER('{name}') and stickername LIKE '{sticker}%';")!=0, "This account already had none of this sticker."
        if count(db, f"Select * from stickers where stickername='{sticker}';")==0:
            stickerid=sql(db, f"select stickerid from stickers where stickername LIKE '{sticker}%';", 2)[0][0]
        else:
            stickerid=sql(db, f"select stickerid from stickers where stickername='{sticker}';", 2)[0][0]
        playerid=sql(db, f"select playerid from players where LOWER(playername)=LOWER('{name}');", 2)[0][0]
        if count(db, f"Select * from inventory where plrid={playerid} and sticker={stickerid};"):
            oldamount=sql(db, f"Select quantity from inventory where plrid={playerid} and sticker={stickerid};",2)[0][0]
            if oldamount>amount:
                sql(db, f"update inventory set quantity={oldamount-amount} where plrid={playerid} and sticker={stickerid};",1)
            else:
                sql(db, f"delete from inventory where plrid={playerid} and sticker={stickerid};",1)
        else:
            sql(db, f"INSERT INTO inventory values ({playerid}, {stickerid}, {amount});",1)
        print(f"Sucessfully removed x{amount} of {sql(db, f'Select stickername from stickers where stickerid={stickerid};', 2)[0][0]} !")
    except Exception as e:
        print(e)


def invaccount(id):
    stickerlist=sql(db, f"SELECT * from inventory where plrid=={id};", 2)
    plrname = sql(db, f"SELECT playername from players where playerid={id};", 2)[0][0]
    print(f"Inventory of {plrname}:")
    for sticker in stickerlist:
        stickername =sql(db, f"SELECT stickername from stickers where stickerid={sticker[1]};", 2)[0][0]
        print(f"x{sticker[2]} {stickername}")

def getstickerfromid(id):
    return sql(db, f"SELECT stickername from stickers where stickerid={id};", 2)[0][0]

def getplrfromid(id):
    return sql(db, f"SELECT playername from players where playerid={id};", 2)[0][0]
def invsticker(id):
    for ids in id:
        ids=ids[0]
        stickerlist=sql(db, f"SELECT * from inventory where sticker=={ids};", 2)
        stickername = getstickerfromid(ids)
        print(f"All {stickername}:")
        for sticker in stickerlist:
            plrname =getplrfromid(sticker[0])
            print(f"x{sticker[2]} {stickername} in {plrname}")


def export():
    print("Keep this text somewhere:")
    print({"Accounts": sql(db, f"SELECT * from players;", 2), "Inventories": sql(db, f"SELECT * from inventory;", 2)})


def imports(text):
    toimport = eval(text)
    sql(db, "DELETE FROM players;", 1)
    sql(db, "DELETE FROM inventory;", 1)
    for e in toimport["Accounts"]:
        sql(db, f"Insert Into players VALUES {e};", 1)
    for e in toimport["Inventories"]:
        sql(db, f"Insert Into inventory VALUES {e};", 1)

    print("Imported !")






while True:
    cmd = str(input("command ? (help for more information)"))
    if cmd=='help':
        print("BSS Stickers Manager V0.2 by YT_valentin \n----------------------\n\n##Accounts:\n" \
        "createaccount: add a roblox account to the database \n" \
        "showaccount: show all accounts created \n" \
        "deleteaccount: delete an account from the database (and all the stickers associated with this account)\n\n"
        "##Selection:\n"
        "invsticker: Show the selected sticker amount on all accounts\n"
        "invaccount: show an account's sticker\nselectaccount: select an account to prevent having to type it for every command\n"
        "inv: Show the inventory of all accounts\n\n"
        "###Add/Remove:\n"
        "addsticker: add the selected amount of a sticker to the selected account\n"
        "removesticker: remove the selected amount of a sticker to the selected account\n\n"
        "###DATA:\n"
        "export: export all your inventories and accounts into text, useful to transfer data when this updates\n"
        "import: import the data exported before to prevent you from entering all of them back when it updates\n"
        "(MAKE SURE NOT TO ENTER SOMEONE ELSE'S DATA IF THE DATA LOOKS DIFFERENT THAN THIS FORMAT: {'Accounts':[stuff], 'Inventories':[stuff]})")
    elif cmd=='createaccount':
        name=str(input("Whats it's roblox name ?"))
        createaccount(name)

    elif cmd=='showaccount':
        showaccount()

    elif cmd=="deleteaccount":
        name=str(input("Whats it's roblox name ?"))
        deleteaccount(name)
    elif cmd=="selectaccount":
        selectedaccount=str(input("Whats it's roblox name ?"))
        if selectedaccount=='':
            selectedaccount
    elif cmd=="addsticker":
        if not selectedaccount:
            name=str(input("Whats it's roblox name ?"))
        else:
            name=selectedaccount
        sticker=str(input("What's the sticker ?"))
        try:
            amount=int(input("How much do you want to add ?"))
        except Exception as e:
            print(e)
            print("Make sure it's a number !!")
        name=sql(db, f"SELECT playername from players where playername LIKE '{name}%';",2)[0][0]
        addsticker(name, sticker, amount)
    elif cmd=="removesticker":
        if not selectedaccount:
            name=str(input("Whats it's roblox name ?"))
        else:
            name=selectedaccount
        sticker=str(input("What's the sticker ?"))
        try:
            amount=int(input("How much do you want to remove ?"))
        except Exception as e:
            print(e)
            print("Make sure it's a number !!")
        name=sql(db, f"SELECT playername from players where playername LIKE '{name}%';",2)[0][0]
        removesticker(name, sticker, amount)

    elif cmd=="invaccount":
        if not selectedaccount:
            name=str(input("Whats it's roblox name ?"))
        else:
            name=selectedaccount
        accid=sql(db, f"SELECT playerid from players where playername LIKE '{name}%';", 2)[0][0]
        invaccount(accid)

    elif cmd=="invsticker":
        name=str(input("Whats the sticker"))
        accid=sql(db, f"SELECT stickerid from stickers where stickername LIKE '{name}%';", 2)
        invsticker(accid)
    elif cmd=="export":
        export()

    elif cmd=="import":
        imported=str(input("Input the data exported before:"))
        imports(imported)
    elif cmd=="inv":
        accid=sql(db, "Select playerid from players;", 2)
        for ids in accid:
            invaccount(ids[0])
    else:
        print("This command doesn't exist, do 'help' to see the list of all of them.")





