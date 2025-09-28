import fetchurl
import json
from Service.ArchiveOrg.history import latest_snapshot
from Service.ArchiveOrg.create import save
from blacklist import inBlacklist
from redirect import finalRedirect

def readExistingFile(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        c = f.read()
    j = json.loads(c)
    return j

def getLatestFile(path):
    oiwikifetch = fetchurl.fetchurl(path)
    all_files =  oiwikifetch.fetchfiles()
    oiwikifetch.fetch()
    return oiwikifetch.url.link

def getArchiveLink(link):
    archiveLink = latest_snapshot(link)
    return archiveLink

def retryUnarchiveLink(data):
    """Some links has been archived for the first time 
    when it was added into the document.
    This function will try to fetch these links.
    """
    updateContent = data
    for key, data in data.items(): #content is a dict
        if data["archiveLink"] == None and inBlacklist(key) == False:
            print("deal with " + key)
            redirectUrl = finalRedirect(key)
            a = latest_snapshot(key)
            if redirectUrl != key:
                b = latest_snapshot(redirectUrl)
            if a != []:
                print(f"write a: {a}")
                updateContent[key]["archiveLink"] = a
            elif b != []:
                print(f"write b: {b}")
                updateContent[key]["archiveLink"] = b
    return updateContent

def main():
    pastContent = readExistingFile('data/data.json')
    pastContent = retryUnarchiveLink(pastContent)
    currentContent = getLatestFile("docs")
    updateContent = {}

    for key, value in currentContent.items():
        if key in pastContent:
        # 去除冗余链接，只保留文档里还存在的链接
            updateContent[key] = pastContent[key]
        elif key.startswith("http"):
            # 处理新增的链接
            print(f"New link: {key}")
            updateContent[key] = value
            if inBlacklist(key) == True:
                updateContent[key]["archiveLink"] = None
                continue
            redirectUrl = finalRedirect(key)
            a = latest_snapshot(key)
            print(f"redirectUrl: {redirectUrl}")
            print(f"key: {key}")
            if redirectUrl != key:
                b = latest_snapshot(redirectUrl)
            if a != []:
                updateContent[key]["archiveLink"] = a
            elif b != []:
                updateContent[key]["archiveLink"] = b
            else:
                # 该链接从未被存档
                print(f"Saving: {key}")
                save(key)
                updateContent[key]["archiveLink"] = None
                
    j = json.dumps(updateContent, indent=4, ensure_ascii=False)
    with open("data/data.json", "w", encoding="utf-8") as f:
        f.write(j)
    # print(j)

if __name__ == "__main__":
    main()