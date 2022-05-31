import pandas as pd
import numpy as np
from tqdm import tqdm, trange
import json
from time import sleep

import api2ch
import html2text
import re
import os

API = api2ch.DvachApi('b')

if os.path.exists("parsed_threads.json"):
    with open("parsed_threads.json", "r") as file:
        PARSED_TREADS = set(json.load(file)["ids"])
else:
    PARSED_TREADS = set()

REPLY_RE = re.compile(">>[0-9]+")

HTML_STRIPPER = html2text.HTML2Text()
HTML_STRIPPER.ignore_links = True
HTML_STRIPPER.ignore_images = True
HTML_STRIPPER.ignore_emphasis = True

def SaveParsed():
    with open("parsed_threads.json", "w") as file:
        json.dump({"ids": list(PARSED_TREADS)}, file)
        
def ThreadGood(thread):
    return thread.reply_count > 20

def AppendDialogues(id, dialogues):
    with open("dialogues.jsonl", "a") as file:
        for dialogue in dialogues:
            json.dump({"id": id, "dialogue": dialogue}, file, ensure_ascii=False)
            file.write("\n")

def FilterAndPrepareText(text):
    text = HTML_STRIPPER.handle(text)
    text = text.lower()
    text = text.replace("\n", " ")
    text = text.replace("(op)", "")
    if text.find("бамп") != -1:
        return
    text = re.sub(' +', ' ', text)
    text = re.sub('^ ', '', text)
    text = re.sub(' $', '', text)
    return text

class Post:
    def __init__(self, idx: int, text: str):
        self.idx = idx
        
        self.parents = []
        while True:
            reply_match = REPLY_RE.match(text)
            if reply_match is not None:
                parent_id = int(reply_match.group(0)[2:])
                span = reply_match.span()
                self.parents.append(parent_id)
                text = text[:span[0]] + text[span[1]:]
                text = re.sub('^ ', '', text)
                text = re.sub(' $', '', text)
            else:
                break
        self.text = text
        
        self.children = []
        self.dialogue = [self.text]
        self.appeared = False
                
    def __repr__(self):
        return {"idx": self.idx, "parents": self.parents, "text": self.text}.__repr__()
    
    def build_random_dialogue(self, context):
        self.appeared = True
        if len(self.dialogue) != 1:
            return self.dialogue
        if len(self.parents) == 0:
            return self.dialogue
        chosen_parent = self.parents[0]
        if chosen_parent in context.keys():
            self.dialogue.extend(context[chosen_parent].build_random_dialogue(context))
        return self.dialogue
            
def BuildDialogues(thread):
    posts = {}
    for post in thread:
        idx = post.num
        text = FilterAndPrepareText(post.comment)
        if text is not None:
            posts[idx] = Post(idx, text)
    
    for _, post in reversed(posts.items()):
        if not post.appeared:
            post.build_random_dialogue(posts)
            
    return [post.dialogue for post in list(posts.values()) if len(post.dialogue) > 1]

def main():
    print("Started collecting...")
    while True:
        while True:
            try:
                board = API.get_board()
                break
            except:
                print(f"Failed to fetch board. Sleeping for 60s")
                sleep(60)
        print("Got board")
            
        for thread in board:
            if thread.num not in PARSED_TREADS and ThreadGood(thread):
                PARSED_TREADS.add(thread.num)
                try:
                    thread = API.get_thread(thread.num)
                except:
                    continue
                dialogues = BuildDialogues(thread)
                AppendDialogues(thread[0].num, dialogues)
        print("Parsed")
        SaveParsed()
        print("Saved. Sleeping for 10m")
        sleep(600)
        
if __name__ == "__main__":
    main()
