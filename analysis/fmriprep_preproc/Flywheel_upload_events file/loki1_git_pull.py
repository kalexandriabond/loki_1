import os
import sys
import git
import shutil

#for FW CLI path
fw_path = open("fw_file_path.txt")
sys.path.insert(0,fw_path)

#To update existing git repo
dir_name = "loki_GitRepo"
remote_url = "https://github.com/kmbond/loki_1.git/"
repo = git.Repo(dir_name)
#origin = repo.create_remote('origin',remote_url).
origin = repo.remote('origin')
origin.pull(origin.refs[0].remote_head)
print ("---Done---")