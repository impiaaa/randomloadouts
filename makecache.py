import os, sys
import warnings
import codecs
if sys.version_info[0] < 3:
    import cPickle as pickle
else:
    import pickle

if sys.platform.startswith('linux'):
    tf_path = os.path.expanduser("~/.local/share/Steam/SteamApps/common/Team Fortress 2/tf/resource/tf_english.txt")
elif sys.platform == 'darwin':
    tf_path = os.path.expanduser("~/Library/Application Support/Steam/SteamApps/common/Team Fortress 2/tf/resource/tf_english.txt")
elif sys.platform.startswith('win'):
    tf_path = os.path.join(os.environ['PROGRAMFILES'], "Steam/SteamApps/common/Team Fortress 2/tf/resource/tf_english.txt")
apikey = open(os.path.expanduser("~/.steamapikey")).read().strip()

def getTranslations():
    translationTable = {}
    for line in codecs.open(tf_path, encoding='utf_16'):
        line = line.strip()
        if line.startswith('#'):
            continue
        elif line.count('"') < 4:
            continue
        else:
            i = line.find('"')+1
            skip = False
            for j in range(i, len(line)):
                if skip:
                    skip = False
                    continue
                if line[j] == '\\':
                    skip = True
                elif line[j] == '"':
                    break
            key = line[i:j].lower()
            i = line.find('"', j+1)+1
            for j in range(i, len(line)):
                if skip:
                    skip = False
                    continue
                if line[j] == '\\':
                    skip = True
                elif line[j] == '"':
                    break
            val = line[i:j]
            translationTable[key] = val
    return translationTable

def makeCache(weaponNames={}):
    import json
    if sys.version_info[0] < 3:
        from urllib2 import urlopen
    else:
        from urllib.request import urlopen
    urldoc = urlopen("http://api.steampowered.com/IEconItems_440/GetSchema/v0001/?key="+apikey)
    data = urldoc.read().decode('utf-8')
    data = json.loads(data)
    urldoc.close()
    itemDB = {} # organized by class, then loadout slot
    itemCount = 0
    
    for item in data["result"]["items"]:
        if "item_slot" not in item:
            continue
        if "craft_class" in item and item["craft_class"] == "": continue
        if item["item_slot"] in ("head", "misc", "action", "taunt", "quest"): continue
        if item["defindex"] in (160, 161, 169, 221, 264, 266, 294, 297, 298, 423, 433, 452, 457, 466, 474, 482, 513, 572, 574, 587, 608, 609, 638, 727, 739, 741, 851, 863, 880, 933, 939, 947, 1013, 1092, 1100, 1102, 1105, 1121, 1123, 1127, 30474, 30667, 30666, 30668, 30665):
            # reskins
            continue
        if item["defindex"] == 850:
            # unavailable
            continue
        if "Festive" in item["name"] or "Botkiller" in item["name"] or "Upgradeable" in item["name"] or "Promo" in item["name"]:
            continue
        newItem = {"item_slot": item["item_slot"],
                   "image_url": item["image_url"],
                   "name": item["name"]}
        if item["item_name"][0] == '#':
            itemName = item["item_name"][1:].lower()
            if itemName in weaponNames: newItem["name"] = weaponNames[itemName]
            else:
                sys.stderr.write("Unknown translation for %s!\n"%item["item_name"])
                continue
        if newItem["name"].startswith("The "):
            newItem["wiki_url"] = "http://wiki.teamfortress.com/wiki/"+newItem["name"][4:].replace(' ', '_')
        else:
            newItem["wiki_url"] = "http://wiki.teamfortress.com/wiki/"+newItem["name"].replace(' ', '_')
        for klass in item.get("used_by_classes", []):
            if item["item_slot"] in ("pda", "pda2", "building") and klass == "Engineer": continue
            if item["item_slot"] == "pda" and klass == "Spy": continue
            if klass not in itemDB:
                itemDB[klass] = {}
            if "per_class_loadout_slots" in item:
                slot = item["per_class_loadout_slots"][klass]
            else:
                slot = item["item_slot"]
            if slot not in itemDB[klass]:
                itemDB[klass][slot] = []
            itemDB[klass][slot].append(newItem)
            print("Added %s used by %s"%(newItem["name"], klass))
        itemCount += 1
    
    out = open("loadoutDB.p", 'wb')
    pickle.dump(itemDB, out, -1)
    out.close()
    
    print("Read %d items" % itemCount)
    return itemDB

if __name__ == "__main__":
    makeCache(getTranslations())
