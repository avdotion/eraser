# Eraser Tool
## Features:
# * Scan selected folder
# * Sort a list of files and folders by date
# * Make a decision:
# ** App can be in exception list
# ** User should confirm all deletion
# ** Files should be divined by file types with low and high priority

## Smart features:
# * Compare archives and folders
# * Exceptions system (hidden file in current folder)


import os
import time
import shutil
from collections import namedtuple

ARCHIVE_EXT = {".zip", ".rar", ".7z"}
EXECUTABLE_EXT = {'.exe', '.com', '.msi'}


class Eraser:
    def __init__(self):
        self.os = None
    
    def scan(self, path):
        def get_folder_size(start_path='.'):
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(start_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
            return total_size
        
        try:
            with open('.erase_tool', 'r') as fin:
                exception_list = [i.rstrip() for i in fin.readlines()]
        except FileNotFoundError:
            exception_list = []
        
        items = {'files': list(), 'folders': list(), 'unknowns': list()}
        for entry in os.listdir(path):
            if entry in exception_list:
                continue
            item = {'name': entry,
                    'linked': False,
                    'excepted': False,
                    'created': os.path.getctime(f'{path}/{entry}')}
            if os.path.isfile(entry):
                item['type'] = 'file'
                item['size'] = os.path.getsize(f'{path}/{entry}')
                items['files'].append(item)
            elif os.path.isdir(entry):
                item['type'] = 'folder'
                item['size'] = get_folder_size(f'{path}/{entry}')
                items['folders'].append(item)
            else:
                item['type'] = 'unknown'
                items['unknowns'].append(item)
            
        return items

    def sort(self, items):
        items['folders'].sort(key=lambda x: x['size'] and x['created'] / x['size'])
        items['files'].sort(key=lambda x: x['size'] and x['created'] / x['size'])
        return items

    def link(self, path, items):
        for i in range(len(items['files'])):
            file = items['files'][i]
            if os.path.splitext(f'{path}/{file["name"]}')[1] in ARCHIVE_EXT:
                for j in range(len(items['folders'])):
                    if items['folders'][j]['name'] == os.path.splitext(file["name"])[0]:
                        items['files'][i]['linked'] = True
                        items['folders'][j]['linked'] = True

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
        for i in range(len(items[exception.type])):
            if items[exception.type][i]['name'] == exception.name:
                items[exception.type][i]['excepted'] = True
        return items

    def erase(self, path, items):
        for folder in items['folders']:
            if not folder['excepted']:
                shutil.rmtree(f'{path}/{folder["name"]}')

        for file in items['files']:
            if not file['excepted']:
                os.remove(f'{path}/{file["name"]}')

    def exclude(self, exception):
        try:
            with open('.erase_tool', 'r') as fin:
                exception_list = [i.rstrip() for i in fin.readlines()]
        except FileNotFoundError:
            exception_list = []
        finally:
            if exception.type == 'folders':
                exception_list.append(f'{exception.name}/')
            elif exception.type == 'files':
                exception_list.append(f'{exception.name}')

            with open('.erase_tool', 'w') as fout:
                for line in exception_list:
                    fout.write(f'{line}\n')


class EraserInterface:
    def __init__(self, path):
        self.tool = Eraser()
        self.path = path
        self.exceptions = []

    def start(self):
        def size_format(size):
            if 0 <= size < 2 ** 10:
                return f'{size}B'
            elif 2 ** 10 <= size < 2 ** 20:
                return f'{size // 2 ** 10}KB'
            elif 2 ** 20 <= size < 2 ** 30:
                return f'{size // 2 ** 20}MB'
            elif 2 ** 30 <= size < 2 ** 40:
                return f'{size // 2 ** 30}GB'
            else:
                return f'{size}B'

        def time_format(delta):
            if delta / 60 / 60 / 24 // 365 > 0:
                return f'more than {(int(delta / 60 / 60 / 24 // 365))} year'
            elif delta / 60 / 60 // 24 > 0:
                return f'more than {(int(delta / 60 / 60 // 24))} days'
            elif delta / 60 // 60 > 0:
                return f'more than {(int(delta / 60 // 60))} hours'
            elif delta // 60 > 0:
                return f'more than {(int(delta // 60))} munites'
            else:
                return f'{(int(delta))} seconds'
        
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
        print('This folders can be deleted:')
        count = 0
        may_be_excepted = list()
    

        Entry = namedtuple('Entry', 'name type')

        for folder in items["folders"]:
            print(f'{count+1}. "{folder["name"]}/" [{time_format(time.time() - folder["created"])}] ({size_format(folder["size"])})')
            if folder['linked']:
                print(f'  * unpacked archive')
            count += 1
            
            may_be_excepted.append(Entry(folder["name"], 'folders'))
        else:
            print()
    
        for file in items["files"]:
            print(f'{count+1}. "{file["name"]}" [{time_format(time.time() - file["created"])}] ({size_format(file["size"])})')
            count += 1
            may_be_excepted.append(Entry(file["name"], 'files'))
        else:
            print()

        print('Type numbers of items you want to add to exceptions:')
        answer = input()
        for exception in answer.split():
            self.tool.exclude(may_be_excepted[int(exception)-1])
            items = self.tool.remove(items, may_be_excepted[int(exception)-1])
        
        self.tool.erase(self.path, items)


if __name__ == "__main__":
    ui = EraserInterface(os.getcwd())
    ui.start()
