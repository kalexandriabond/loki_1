import os
import sys
import git
import shutil

#for FW CLI path
fw_path = open("fw_file_path.txt")
sys.path.insert(0,fw_path)

#To clone Git Repo for the first time

dir_name = "loki_GitRepo"
remote_url = "https://github.com/kmbond/loki_1.git/"

if os.path.isdir(dir_name):
    shutil.rmtree(dir_name)
    
os.mkdir(dir_name)
print("In process")

repo = git.Repo.init(dir_name)
origin = repo.create_remote('origin',remote_url)
print("Added remote")
print("Fetching")
origin.fetch()
print ("Fetching complete")
origin.pull(origin.refs[0].remote_head)
print ("---Done---")

