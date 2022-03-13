import os
import sys
import json

from operator import attrgetter

with open("New_Albion_Beautified.json") as o:
    file = json.load(o)
    
class Message(object):
    mid = 0
    party = None
    content = ''
    author = {
        "aid":"0",
        "sheet":"0",
        "name":""
    }
    tone = ''
    created = ''
    whisperedto = []
    isdescription = False
    isstorytelling = False
    
    def __init__(self, dictionary):
        self.mid = dictionary['mid']
        self.party = dictionary['pid']
        self.content = dictionary['content']
        self.aid = dictionary['aid']
        self.sheet = dictionary['sheet']
        self.name = dictionary['name']
        self.tone = dictionary['tone']
        self.whisperedto = dictionary['whisperedto']
        self.created = dictionary['created']
        self.isdescription = dictionary['isdescription']
        self.isstorytelling = dictionary['isstorytelling']
        
    def read(self):
        values = {
            'mid':self.mid,
            'pid':self.party,
            'content':self.content,
            'aid':self.aid,
            'sheet':self.sheet,
            'name':self.name,
            'tone':self.tone,
            'whisperedto':self.whisperedto,
            'created':self.created,
            'isdescription':self.isdescription,
            'isstorytelling':self.isstorytelling
        }
        return values

def NewMessage(dictionary):
    message = Message(dictionary)
    return message
    
# Roll class

message = {}
Messages = []
partyid = None
limiter = 0
for party in file: # Each party has a party and a content division. This splits the file up into parties (party/content pairs)
    if isinstance(party, dict): # Each segment of a party/content division is a dictionary
        for key, values in party.items():
            if key == 'party': # Here we get each party's id number
                if values != None:
                    partyid = values['id']
                else:
                    partyid = None
            elif key == 'content': # Here we parse the actual content of the parties. Each 'field' is a message or a roll.
                for field in values:
                    if limiter > 20:
                        break
                    if isinstance(field, dict):
                        message.update({
                            'mid':f"{field.setdefault('id', None)}",
                            'pid':f"{partyid}",
                            'content':f"{field.setdefault('content', None)}",
                            'tone':f"{field.setdefault('tone', None)}", # No tone is already stored as str('None'), so asking if message.tone == None will always be false. Instead check message.tone == "None"
                            'whisperedto':f"{str(field.setdefault('whispered_to', None)).replace('[','').replace(']','')}",
                            'created':f"{field.setdefault('created', None)}",
                            'isdescription':f"{field.setdefault('is_description', False)}",
                            'isstorytelling':f"{field.setdefault('is_storytelling', None)}"
                        })
                        if 'author' in field:
                            message.update({
                                'aid':f"{field['author'].setdefault('id', None)}",
                                'sheet':f"{field['author'].setdefault('sheet', None)}",
                                'name':f"{field['author'].setdefault('name_then', None)}"
                            })
                        else:
                            message.update({
                                'aid':None,
                                'sheet':None,
                                'name':None
                            })
                    m = NewMessage(message)
                    Messages.append(m)
                    limiter += 1
mss = 0
Messages.sort(key=attrgetter('mid'))
with open("printout.txt", "w") as p:
    while mss < len(Messages):
        r = Messages[mss]
        if r.aid == None:
            p.writelines(f"     Narrator (description): {r.content}\n")
        elif r.isdescription == True:
            p.writelines(f"     {r.name} (description): {r.content}\n")
        elif r.tone != "None":
            p.writelines(f"     {r.name} ({r.tone}): {r.content}\n")
        else:
            p.writelines(f"     {r.name}: {r.content}\n")
        mss += 1