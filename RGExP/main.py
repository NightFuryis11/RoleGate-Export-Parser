import os
import sys
import json
from datetime import datetime
import pickle
import re

from operator import attrgetter


def parseCreation(string):
    creation = string.split("T")
    creationDate = creation[0]
    creationTime = creation[1] #"2020-07-24T10:06:47.581655Z"
    creationDate1 = list(map(int, creationDate.split("-")))
    creationTime1 = creationTime.split(".")
    creationTime2 = list(map(int, str(creationTime1[0]).split(":")))
    time = []
    for x in creationDate1:
        time.append(x)
    for x in creationTime2:
        time.append(x)
    cm = datetime(time[0], time[1], time[2], time[3], time[4], time[5])
    return cm

class Message(object):
    def __init__(self, dictionary):
        self.id = None if dictionary['mid'] is None else int(dictionary['mid'])
        self.party = dictionary['party']
        self.content = dictionary['content']
        self.author = dictionary['author']
        self.tone = dictionary['tone']
        self.toldto = None
        if dictionary['whisperedto'] != None:
            self.whisperedto = [int(x) for x in dictionary['whisperedto']]
        else:
            self.whisperedto = None
        self.action = dictionary['action']
        self.created = parseCreation(dictionary['created'])
        self.isdescription = bool(dictionary['isdescription'])
        self.isstorytelling = bool(dictionary['isstorytelling'])

        if dictionary['result'] != None:
            self.result = []
            for x in dictionary['result']:
                if type(x) is list:
                    for y in x:
                        if type(y) != int:
                            self.result.append(y)
                        else:
                            self.result.append(int(y))
                elif type(x) is int:
                    self.result = x
                elif x == 'success':
                    self.result = 'success'
        else:
            self.result = None
        self.mtype = dictionary['mtype']
        
        #print(self.result, self.id, self.party.id, self.created)
        
    def read(self):
        # Returns dictionary of all values stored within the Message object
        values = {
            'mid':self.id,
            'pid':self.party.id,
            'content':self.content,
            'aid':self.author.id,
            'sheet':self.author.sheet,
            'name':self.author.name,
            'tone':self.tone,
            'toldto':self.toldto,
            'whisperedto':self.whisperedto,
            'action':self.action,
            'created':self.created,
            'isdescription':self.isdescription,
            'isstorytelling':self.isstorytelling,
            'result':self.result,
            'mtype':self.mtype
        }
        return values
    
    def whisper(self, authorList):
        lis = []
        w = self.whisperedto
        if w != None:
            for y in w:
                lis.append(next((x for x in authorList if x.id == y), None))
            self.whisperedto = lis
        return self
    
    #next((x for x in test_list if x.value == value), None)
    
    def whisperTarget(self):
        s = ''
        if self.whisperedto != None:
            for a in self.whisperedto:
                if a != None:
                    s = s + f"{a.name}, "
            s = s[:-2]
            return s
        else:
            return None
        
    def tell(self, authorList):
        contentRead = self.content
        tell = []
        temp = []
        ongoing = True
        while ongoing:
            if contentRead[0] == '@':
                poundindex = contentRead.find("#") + 1
                if poundindex == 0:
                    break
                endindex = re.search(r"\D", contentRead[poundindex:])
                endindex = endindex.start() + poundindex
                tags = contentRead[:endindex]
                tag = list(tags.replace("@", "").split("#"))
                for x in authorList:
                    if x not in tell:
                        if (x.id == int(tag[1])) and (x.name == tag[0]):
                            tell.append(x)
                message = contentRead[endindex:]
                contentRead = message
                self.toldto = tell
            else:
                ongoing = False
        self.content = contentRead
        return self
    
    def tellTarget(self):
        s = ''
        if self.toldto != None:
            for a in self.toldto:
                s = s + f"{a.name}, "
            s = s[:-2]
        return s
        

def NewMessage(dictionary):
    message = Message(dictionary)
    return message
        
class Author(object):
    def __init__(self, dictionary):
        self.id = None if dictionary['aid'] is None else int(dictionary['aid'])
        self.sheet = None if dictionary['sheet'] is None else int(dictionary['sheet'])
        self.name = dictionary['name']
        self.appearances = []
        
    def getID(self):
        aid = self.id
        return aid
    
    def getName(self):
        name = self.name
        return name
    
    def read(self, fineDetail = False):
        values = {
            "id":self.id,
            "sheet":self.sheet,
            "name":self.name
        }
        if fineDetail:
            values.update({
                "appearances":self.appearances
            })
        return values
    
    def addLine(self, line):
        self.appearances.append(int(line))
        return self
    
def NewAuthor(dictionary):
    author = Author(dictionary)
    return author
    
class Party(object):
    def __init__(self, dictionary):
        self.id = None if dictionary['pid'] is None else int(dictionary['pid'])
        self.name = dictionary['name']
        if dictionary['characters'] != None:
            d = dictionary['characters'].replace('[','').replace(']','').split(', ')
            self.characters = [int(x) for x in d]
        else:
            self.characters = None
        self.first_line = None if dictionary['linef'] is None else int(dictionary['linef'])
        self.last_line = None if dictionary['linel'] is None else int(dictionary['linel'])
        
    def getID(self):
        pid = self.id
        return pid
    
    def getBounds(self):
        bounds = [self.first_line, self.last_line]
        return bounds
    
    def read(self):
        values = {
            "id":self.id,
            "name":self.name,
            "characters":self.characters,
            "linef":self.first_line,
            "linel":self.last_line
        }
        return values
    
def NewParty(dictionary):
    party = Party(dictionary)
    return party

def save_object(obj, filename):
    with open(filename, 'wb') as outp:
        pickle.dump(obj, outp, -1)

def picklepack(gname):
    
    with open(f"{gname}.json") as o:
        file = json.load(o)
    
    message = {}
    party = {}
    author = {}
    Messages = []
    Authors = []
    Parties = []
    partyid = None
    limiter = 0
    for party in file: # Each party has a party and a content division. This splits the file up into parties (party/content pairs)
        if isinstance(party, dict): # Each segment of a party/content division is a dictionary
            for key, values in list(party.items()):
                if key == 'party': # Here we get each party's id number
                    if values != None:
                        party.update({
                            'pid':f"{values.setdefault('id', None)}",
                            'name':f"{values.setdefault('name', None)}",
                            'characters':f"{values.setdefault('characters', None)}",
                            'linef':f"{values.setdefault('separation_line_id', None)}",
                            'linel':f"{values.setdefault('closing_line_id', None)}"
                        })
                    else:
                        party.update({
                            'pid':None,
                            'name':None,
                            'characters':None,
                            'linef':None,
                            'linel':None
                        })
                    partyid = party['pid']
                    g = NewParty(party)
                    Parties.append(g)
                elif key == 'content': # Here we parse the actual content of the parties. Each 'field' is a message or a roll.
                    for field in values:
                        if isinstance(field, dict):
                            rollRes = []
                            message.update({
                                'mid':f"{field.setdefault('id', None)}",
                                'party':g,
                                'content':f"{field.setdefault('content', None)}",
                                'tone':f"{field.setdefault('tone', None)}", # No tone is already stored as str('None'), so asking if message.tone == None will always be false. Instead check message.tone == "None"
                                'whisperedto':field.setdefault('whispered_to', None),
                                'created':f"{field.setdefault('created', None)}",
                                'isdescription':f"{field.setdefault('is_description', False)}",
                                'isstorytelling':f"{field.setdefault('is_storytelling', None)}"
                            })
                            if 'author' in field:
                                author.update({
                                    'aid':f"{field['author'].setdefault('id', None)}",
                                    'sheet':f"{field['author'].setdefault('sheet', None)}",
                                    'name':f"{field['author'].setdefault('name_then', None)}"
                                })
                            else:
                                author.update({
                                    'aid':None,
                                    'sheet':None,
                                    'name':None
                                })
                            k = NewAuthor(author)
                            b = next((x for x in Authors if (x.id == k.id) and (x.name == k.name)), None)
                            if b == None:
                                Authors.append(k)
                            else:
                                k = b
                            k = k.addLine(int(message['mid']))
                            message.update({
                                'author':k
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
                            else:
                                message.update({
                                    'result':None,
                                    'mtype':'message'
                                })
                        m = NewMessage(message).tell(Authors).whisper(Authors)
                        Messages.append(m)
    global data                
    data = {
        "parties":Parties,
        "authors":Authors,
        "messages":Messages
    }
    
    save_object(data, f'{gname}_extracted_data.pkl')
    
    
def pickle_loader(filename):
    with open(filename, "rb") as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break

def pickleunpack(dname):
    for a in pickle_loader(f'{dname}_extracted_data.pkl'):
        Parties = a['parties']
        Authors = a['authors']
        Messages = a['messages']
        
    mss = 0
    Messages.sort(key=lambda x: int(x.id))
    with open(f"{dname}_printout.txt", "w") as i:
        while mss < len(Messages):
            e = Messages[mss]
            if e.mtype == 'message':
                if e.whisperedto == None:
                    if e.toldto == None:
                        if e.author.id == None:
                            i.writelines(f"     Narrator (description): {e.content}\n")
                        elif e.isdescription == True:
                            i.writelines(f"     {e.author.name} (description): {e.content}\n")
                        elif e.tone != "None":
                            i.writelines(f"     {e.author.name} ({e.tone}): {e.content}\n")
                        else:
                            i.writelines(f"     {e.author.name}: {e.content}\n")
                    else:
                        if e.author.id == None:
                            i.writelines(f"     Narrator (description) to {e.tellTarget()}: {e.content}\n")
                        elif e.isdescription == True:
                                i.writelines(f"     {e.author.name} (description) to {e.tellTarget()}: {e.content}\n")
                        elif e.tone != "None":
                            i.writelines(f"     {e.author.name} ({e.tone}) to {e.tellTarget()}: {e.content}\n")
                        else:
                            i.writelines(f"     {e.author.name} to {e.tellTarget()}: {e.content}\n")
                else:
                    if e.author.id == None:
                        i.writelines(f"     Narrator (description) whispered to {e.whisperTarget()}: {e.content}\n")
                    elif e.isdescription == True:
                        i.writelines(f"     {e.author.name} (description) whispered to {e.whisperTarget()}: {e.content}\n")
                    elif e.tone != "None":
                        i.writelines(f"     {e.author.name} ({e.tone}) whispered to {e.whisperTarget()}: {e.content}\n")
                    else:
                        i.writelines(f"     {e.author.name} whispered to {e.whisperTarget()}: {e.content}\n")
            elif e.mtype == 'roll':
                if e.author.id == None:
                    if e.action != None:
                        i.writelines(f"     <Roll> Narrator rolls {e.content} as '{e.action}' with final result of {str(e.result).replace('[','').replace(']','')}.\n")
                    else:
                        i.writelines(f"     <Roll> Narrator rolls {e.content} with final result of {str(e.result).replace('[','').replace(']','')}.\n")
                else:
                    if e.action != None:
                        i.writelines(f"     <Roll> {e.author.name} rolls {e.content} as '{e.action}' with final result of {str(e.result).replace('[','').replace(']','')}.\n")
                    else:
                        i.writelines(f"     <Roll> {e.author.name} rolls {e.content} with final result of {str(e.result).replace('[','').replace(']','')}.\n")
            mss += 1