import os
import time
import shutil
ARCHIVE_EXT = {".zip", ".rar", ".7z"}
EXECUTABLE_EXT = {'.exe', '.com', '.msi'}


class Eraser:
    def __init__(self):
        pass

    def scan_files(self, file_type):
        found = list()
        for node in os.listdir():
            if os.path.isfile(node):
                if file_type == "all":
                    found.append(node)
                else:
                    if node[node.rindex('.'):] in file_type:
                        found.append(node)
        return found

    def scan_folders(self):
        found = list()
        for node in os.listdir():
            if os.path.isdir(node):
                found.append(node)
        return found

    def scan_unzipped(self, found):
        unzipped = list()
        for node in found:
            if node[:node.rindex('.')] in os.listdir():
                unzipped.append(node)
        return unzipped

    def scan_time(self, found):
        d = dict()
        for node in found:
            d[node] = int(os.path.getatime(node))
        return sorted(d.items(), key=lambda x: x[1])

    def delete(self, files, mode):
        if mode == "file":
            for file in files:
                os.remove(file)
        elif mode == "folder":
            for folder in files:
                shutil.rmtree(folder)


class Interface:
    def __init__(self):
        self.task = Eraser()

    def start(self):
        print('Select mode of cleaning:')
        print('1. Easy clean (automatic old files detection)')
        print('2. Deep clean')
        cmd = input('Type 1 or 2: ')
        if cmd == '1':
            print()
            self.easy_clean()
        elif cmd == '2':
            print()
            self.deep_clean()

    def easy_clean(self):
        print('Scanning for unzipped archives...')
        found = self.task.scan_files(ARCHIVE_EXT)
        print(len(found), 'archives was found.')
        unzipped = self.task.scan_unzipped(found)
        print(len(unzipped), 'of them are unzipped to the same directory.')
        if len(unzipped):
            cmd = input('Delete them? (y/n): ')
            if cmd == 'y':
                self.task.delete(unzipped, "file")
                print(len(unzipped), 'archives was deleted')
        print()
        print('Looking for old executable files...')
        found = self.task.scan_files(EXECUTABLE_EXT)
        print(len(found), 'executables was found.')
        found = self.task.scan_time(found)
        self.selective_delete(found, "file")
        print()
        print('Looking for old folders...')
        found = self.task.scan_folders()
        print(len(found), 'folders was found.')
        found = self.task.scan_time(found)
        self.selective_delete(found, "folder")
        print()
        print("Use deep scan to delete more.")

    def deep_clean(self):
        print("Looking for all files...")
        self.selective_delete(self.task.scan_time(self.task.scan_files("all")), "files")

    def time_output(self, delta):
        if delta / 60 / 60 / 24 // 365 > 0:
            return 'more than ' + str(int(delta / 60 / 60 / 24 // 365)) + ' year'
        elif delta / 60 / 60 // 24 > 0:
            return 'more than ' + str(int(delta / 60 / 60 // 24)) + ' days'
        elif delta / 60 // 60 > 0:
            return 'more than ' + str(int(delta / 60 // 60)) + ' hours'
        elif delta // 60 > 0:
            return 'more than ' + str(int(delta // 60)) + ' munites'
        else:
            return str(int(delta)) + ' seconds'


    def selective_delete(self, data, mode):
        for archive in data:
            print(archive[0], '- last accessed', self.time_output(time.time() - archive[1]))
            ans = input('Are you sure to delete this file (y/n): ')
            print()
            if ans == 'y':
                self.task.delete([archive[0]], mode)
            elif ans == 'n':
                pass
            else:
                return


if __name__ == "__main__":
    i = Interface()
    i.start()
