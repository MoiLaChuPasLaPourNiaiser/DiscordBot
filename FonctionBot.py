from datetime import datetime, date, timedelta

chemin = "pointsDataBase.txt"
cheminCriminelle = "criminelleRecords.txt"
timeFree = 30
returnIfFree = timedelta(minutes=0)
returnIfCriminalNotFound = timedelta(minutes=-1)

# Aller chercher tous les éléments de la database
def getNamesAndPoints() :
    records = []
    with open(chemin, 'r') as f :
        allNameAndPoints = f.readlines()
    for i in allNameAndPoints :
        record = i.strip().split(',')
        user = {
            "name" : record[0],
            "points" : int(record[1]),
            "lastMessageDate" : datetime.strptime(record[2], "%Y-%m-%d").date()
        }
        records.append(user)
    return records

# Aller chercher un user dans la liste de tous les user
def getNameAndPoints(p_name) :
    allNamesAndPoints = getNamesAndPoints()
    for i in allNamesAndPoints :
        if(i["name"] == p_name) :
            return i
    return {"name" : "None"}

# Fonction pour ajouter un certain nombre de points à un certain user
def addPoints (p_name, p_points) : 
    found = False
    records = getNamesAndPoints()
    for l in records :
        if (l["name"] == p_name) :
            found = True
            nowPoint = l["points"] + p_points
            l["points"] = nowPoint
            break
    if found :
        with open(chemin, 'w') as f :
            f.writelines(record["name"] + "," + str(record["points"]) + "," + str(date.today()) + "\n" for record in records)
    else :
        with open(chemin, 'a') as f : 
            f.write(p_name + "," + str(p_points) + "," + str(date.today()) + "\n")
    
def verifyPseudo(p_pseudo, p_pseudos):
    for i in p_pseudos:
        if(i == p_pseudo):
            return True
    return False

def addCriminelle(p_pseudo):
    with open (cheminCriminelle, 'a') as f:
        f.write(p_pseudo + "," + str(datetime.now()) + "\n")    

def removeCriminelle(p_pseudo):
    with open(cheminCriminelle, 'r') as f:
        criminelles = f.readlines()
        for i in criminelles:
            criminelle = i.strip().split(',')
            if(criminelle[0] == p_pseudo):
                diff = datetime.now() - datetime.strptime(criminelle[1], "%Y-%m-%d %H:%M:%S.%f")
                if(diff >= timedelta(minutes=timeFree)):
                    criminelles.remove(i)
                    with open(cheminCriminelle, 'w') as g:
                        g.writelines(criminelles)
                    return returnIfFree
                else:
                    return timeFree - int(diff.total_seconds() / 60)
        return returnIfCriminalNotFound
    
def verifyPrice(p_price, p_name):
    user = getNameAndPoints(p_name)
    if(user["name"] != "None"):
        if(user["points"] >= p_price):
            return True
    return False

def pay(p_pseudo, p_price):
    allPeople = getNamesAndPoints()
    for i in allPeople:
        if(i["name"] == p_pseudo):
            i["points"] = i["points"] - p_price
    with open(chemin, 'w') as f:
        f.writelines(people["name"] + "," + str(people["points"]) + "," + str(people["lastMessageDate"]) + "\n" for people in allPeople)
    