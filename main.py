# Eraser Tool
## Features:
# * Scan selected folder
# * Sort a list of files and folders by date
# * Make a decision:
# ** App can be in exception list
# ** User should confirm all deletion
# ** Files should be divined by file types with low and high priority

import os
import time
import shutil

ARCHIVE_EXT = {"zip", "rar", "7z"}
EXECUTABLE_EXT = {'exe', 'com', 'msi'}


class Eraser:
    def __init__(self):
        self.os = None
    
    def scan(self, path):
        items = {'files': list(), 'folders': list(), 'unknowns': list(), 'linked': False}
        for entry in os.listdir(path):
            item = {'name': entry, 'created': os.path.getctime(path + entry)}
            if os.path.isfile(entry):
                item['type'] = 'file'
                items['files'].append(item)
            elif os.path.isdir(entry):
                item['type'] = 'folder'
                items['folders'].append(item)
            else:
                item['type'] = 'unknown'
                items['unknowns'].append(item)
            
        return items

    def sort(self, items):
        items['folders'].sort(lambda x: x['created'])
        items['files'].sort(lambda x: x['created'])
        return items

    def link(self, path, items):
        for i in range(len(items['files'])):
            file = items['files'][i]
            if file.os.path.splitext(path + file['name'])[1] in ARCHIVE_EXT:
                for folder in items['folders']:
                    if folder['name'] == file['name']:
                        items['files'][i]['linked'] = True
                        items['folders'][i]['linked'] = True

        return items
    
    def resolve(self, exceptions, items):
        for i in range(len(items['files'])):
            if items['files'][i] in exceptions:
                items['files'][i]['excepted'] = True
        for i in range(len(items['folders'])):
            if items['folders'][i] in exceptions:
                items['folders'][i]['excepted'] = True
        
        return items
    
    def remove(self, items, exception):
        exp_name, exp_type = exception
        for i in range(len(items[exp_type])):
            if items[exp_type][i]['name'] == exp_name:
                items[exp_type][i]['name']['except'] = True
        return items

    def erase(self, path, items):
        for folder in items['folders']:
            shutil.rmtree(path + folder['name'])

        for file in items['files']:
            os.remove(path + file['name'])


class EraserInterface:
    def __init__(self):
        self.tool = Eraser()
        self.path = None
        self.exceptions = None

    def start(self):
        # Launch scaning
        print('Scaning launched...')
        items = self.tool.scan(self.path)
        print(f'Scaning finished ({len(items["folders"])} folders and {len(items["files"])} files)')
        
        # Sort items by date created
        items = self.tool.sort(items)

        # Link packed and unpacked archives
        items = self.tool.link(self.path, items)

        # Resolve issues if files in 'exceptions'
        items = self.tool.resolve(self.exceptions, items)

        # Do the first decision
        print('This folder should be deleted:')
        count = 0
        may_be_excepted = list()
        
        for folder in items["folders"]:
            print(f'{count}. "{folder["name"]}/" ({folder["size"]})')
            count += 1
            may_be_excepted.append((folder["name"], 'folder', ))
        for file in items["files"]:
            print(f'{count}. "{file["name"]}" ({file["size"]})')
            count += 1
            may_be_excepted.append((folder["name"], 'file', ))
        
        print('Type numbers of items you want to add to exceptions:')
        answer = input()
        for exception in answer.split():
            items = self.tool.remove(items, may_be_excepted[exception])
        
        self.tool.erase(self.path, items)


if __name__ == "__main__":
    ui = EraserInterface()
    ui.start()
