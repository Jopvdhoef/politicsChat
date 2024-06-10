import requests
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import sys

def parseXML(file, politician):
    root = ET.fromstring(file)
    prefix = root.tag.split('}')[0] + '}'
    tree = ET.ElementTree(root)
    newRoot = ET.Element('data')
    cwd = os.getcwd()
    targetPath = os.path.join(cwd, politician + '/')
    while not os.path.exists(targetPath):
        os.mkdir(targetPath)

    data = []
    for elem in tree.iter(prefix + 'activiteitdeel'):
        name = elem.find("./" + prefix + "spreker/" + prefix + "achternaam")
        if name != None and name.text == politician:
            data.append(elem)

    if len(data) > 0:
        title = root.find("./" + prefix + "vergadering/" + prefix + "titel")
        f = open(targetPath + title.text + '.xml', 'w')
        for elem in data:
            newRoot.append(elem)

        xmlstr = minidom.parseString(ET.tostring(newRoot)).toprettyxml()
        f.write(xmlstr)
        f.close()
        print(title.text)

def collect(request, politician, pages):
    if pages > 0:
        raw = request.json()
        meetings = raw['value']

        doc_id = ""
        for meeting in meetings:
            # Get a list of all the documents of one meeting
            meetingDocuments = requests.get("https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag?$filter=Vergadering_Id%20eq " + meeting['Id']).json()['value']
            for doc in meetingDocuments:
                if doc['Soort'] == 'Eindpublicatie':
                    doc_id = doc['Id']
                    xml = requests.get("https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag(" + doc_id + ")/resource").content
                    parseXML(xml, politician)
                    break
                else:
                    doc_id = ""
                    continue
        pages -= 1
        next = raw['@odata.nextLink']
        collect(requests.get(next), politician, pages)
    else:
        return

def main():
    politician = sys.argv[1]
    pages = int(sys.argv[2])
    request = requests.get("https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Vergadering?$orderBy=Datum%20desc")
    collect(request, politician, pages)
    print('Done')

if __name__ == "__main__":
    main()



