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
    action = ''
    created = ''
    whisperedto = []
    isdescription = False
    isstorytelling = False
    result = []
    mtype = ''
    
    def __init__(self, dictionary):
        self.mid = dictionary['mid']
        self.party = dictionary['pid']
        self.content = dictionary['content']
        self.aid = dictionary['aid']
        self.sheet = dictionary['sheet']
        self.name = dictionary['name']
        self.tone = dictionary['tone']
        self.whisperedto = dictionary['whisperedto']
        self.action = dictionary['action']
        self.created = dictionary['created']
        self.isdescription = dictionary['isdescription']
        self.isstorytelling = dictionary['isstorytelling']
        self.result = dictionary['result']
        self.mtype = dictionary['mtype']
        
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
            'action':self.action,
            'created':self.created,
            'isdescription':self.isdescription,
            'isstorytelling':self.isstorytelling,
            'result':self.result,
            'mtype':self.mtype
        }
        return values

def NewMessage(dictionary):
    message = Message(dictionary)
    return message

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
                    #if limiter > 202:
                    #    break
                    if isinstance(field, dict):
                        rollRes = []
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
                        if 'action' in field:
                            for a in field['action']:
                                message.update({
                                    'action':field['action'][a]
                                })
                        else:
                            message.update({
                                'action':None
                            })
                        if 'pools' in field:
                            for p in field['pools']:
                                if 'final_result' in p:
                                    rollRes.append(p['final_result'])
                                    message.update({
                                        'result':rollRes
                                    })
                                else:
                                    for z in p['rolls']:
                                        if 'modifier' in p:
                                            for val in z['final_result']:
                                                vals = val + p['modifier']
                                                rollRes.append(vals)
                                                message.update({
                                                    'result':rollRes
                                                })
                                        else:
                                            rollRes.append(z['final_result'])
                                            message.update({
                                                'result':rollRes
                                            })
                            message.update({
                                'mtype':'roll'
                            })
                                        #print(message['mid'], (q['final_result'] + p['rolls']['modifier']), message['created'], limiter)
                                        
                                
                        else:
                            message.update({
                                'result':None,
                                'mtype':'message'
                            })
                        
                    m = NewMessage(message)
                    Messages.append(m)
                    limiter += 1
mss = 0
Messages.sort(key=attrgetter('mid'))
with open("printout.txt", "w") as i:
    while mss < len(Messages):
        e = Messages[mss]
        if e.mtype == 'message':
            if e.aid == None:
                i.writelines(f"{mss}     Narrator (description): {e.content}\n")
            elif e.isdescription == True:
                i.writelines(f"{mss}     {e.name} (description): {e.content}\n")
            elif e.tone != "None":
                i.writelines(f"{mss}     {e.name} ({e.tone}): {e.content}\n")
            else:
                i.writelines(f"{mss}     {e.name}: {e.content}\n")
        elif e.mtype == 'roll':
            if e.aid == None:
                if e.action != None:
                    i.writelines(f"{mss}     <Roll> Narrator rolls {e.content} as '{e.action}' with final result of {str(e.result).replace('[','').replace(']','')}.\n")
                else:
                    i.writelines(f"{mss}     <Roll> Narrator rolls {e.content} with final result of {str(e.result).replace('[','').replace(']','')}.\n")
            else:
                if e.action != None:
                    i.writelines(f"{mss}     <Roll> {e.name} rolls {e.content} as '{e.action}' with final result of {str(e.result).replace('[','').replace(']','')}.\n")
                else:
                    i.writelines(f"{mss}     <Roll> {e.name} rolls {e.content} with final result of {str(e.result).replace('[','').replace(']','')}.\n")
        mss += 1