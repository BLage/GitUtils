import os
import json
import subprocess, shlex
from urllib.request import urlopen
from urllib.parse import urlparse
from urllib.parse import unquote
from datetime import datetime

pagesize = 100
token = "<TOKEN>"
gitserver = "<GITLABSERVER>"
basefolder = "<BASE FOLDER>"
currentFolder = os.getcwd()

pageurltemplate = "{}/api/v4/projects?private_token={}&per_page={}&page={}"

total = 0
current_time = datetime.now().strftime("%H_%M_%S")
f=open(f"{currentFolder}/notdownloaded{current_time}.csv", "a+")

def loadPagedProjects(page):
    pageurl = pageurltemplate.format(gitserver, token, pagesize, page + 1)
    print(f"Getting {pagesize} from page {page + 1} - {pageurl}")
    pageProjects = urlopen(pageurl)
    pageProjectsDict = json.loads(pageProjects.read().decode())
    for idx, project in enumerate(pageProjectsDict):
        current = idx + (page*100)
        projectRepoUrl  = project['http_url_to_repo']
        try:
            if "owner" in project:
                print(f"\t{total}/{current}.skipped {projectRepoUrl}")
                status = "skipped"
            else:
                print(f"\t{total}/{current}.Repo... - {projectRepoUrl}")
                folder = basefolder + unquote(urlparse(projectRepoUrl).path)

                if os.path.exists(folder):
                    print("ALERT!!!! RMDIR "+ folder + " /S /Q")

                os.makedirs(folder, mode=0o777, exist_ok=True)
                projectGitClone = f'git clone {projectRepoUrl} {folder}'
                command = shlex.split(projectGitClone)

                print(f"\t{total}/{current}.Starting... - {projectGitClone}")
                subprocess.Popen(command).wait()
                print(f"\t{total}/{current}.End. - {projectGitClone}")
                status = "cloned"
        except Exception as e:
            print("Error on {}: {}".format(projectRepoUrl, e))
            status = "error" + e

        f.write(f"{projectRepoUrl}, {status}\r\n")

allProjects = urlopen(pageurltemplate.format(gitserver, token, pagesize, 1))
pages = allProjects.headers.get("X-Total-Pages")
total = allProjects.headers.get("X-Total")

print(f"Total {total} (Pages {pages})")

for page in range(0, int(pages)):
    try:
        loadPagedProjects(page)
    except Exception as e:
        print(f"Error on {page}: {e}")
        raise

f.close()
print("finished downloading all gitlab!!!!")
