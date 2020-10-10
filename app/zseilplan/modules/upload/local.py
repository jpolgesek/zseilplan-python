import os
import shutil 

class Uploader:
    do_not_upload = [
        "manifest.json",
        "index.html",
        "update.html"
    ]

    def __init__(self, hostname: str):
        self.hostname = hostname
        return
            
    def connect(self):
        return True

    def chdir(self, directory: str):
        self.cd = directory
        return

    def ls(self):
        return os.listdir(self.cd)

    def mkdir(self, directory: str):
        try:
            os.mkdir(directory)
        except:
            return False
        return True

    def copytree(self, src, dst, symlinks=False, ignore=None): 
        for item in os.listdir(src): 
            s = os.path.join(src, item) 
            d = os.path.join(dst, item) 
            if os.path.isdir(s): 
                if os.path.isdir(d): 
                    self.copytree(s, d, symlinks, ignore) 
                else: 
                    shutil.copytree(s, d, symlinks, ignore) 
            else: 
                shutil.copy2(s, d)

    
    def fetch_file(self, filename, mode="r"):
        filename = os.path.join(self.cd, filename)
        with open(filename, mode) as f:
            data = f.read()
        return data
    
    def upload_file(self, source, target):
        target = os.path.join(self.cd, target)
        shutil.copyfile(source, target)
        return

    def upload_dir(self, source, target):
        target = os.path.join(self.cd, target)
        self.copytree(source, target)
        return