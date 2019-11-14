from github import Github
from urlparse import urljoin
import threading
import time
import requests
import json
import argparse
import os

parser = argparse.ArgumentParser(
        description='Git Secrets alerts'
    )

parser.add_argument(
        '--orgname',
        help='Proivde Organisation Name',
        required=False,
        default="grofers"
    )
args = parser.parse_args()

access_token = os.getenv('access_token') //export the github access token
g = Github(access_token)
Headers = {'Authorization': 'token {}'.format(access_token),
           'Accept': 'application/vnd.github.v3+json'
        }
org_repo = list()
org_mem_list = list()
collab_list = list()
search_user_list = list()
user_repo_list = list()
url_dict = dict()

def member_list():
    URL = "https://api.github.com/orgs/"+args.orgname+"/members"
    page = 1
    while True:
        full_url = URL+"?page="+str(page)
        page += 1
        req = requests.get(full_url, headers=Headers)
        repos = json.loads(req.text)
        #print repos
        if len(repos) == 0: # When last page encountered
            break
        for repo in repos:
            org_mem_list.append(repo['login'])
    print org_mem_list


def search_user():
    URL = "https://api.github.com/search/users?q="+args.orgname+"&page="
    page = 1
    while True:
        full_url = URL+str(page)
        print(full_url)
        page += 1
        req = requests.get(full_url, headers=Headers)
        repos = json.loads(req.text)
        if len(repos['items']) == 0: # When last page encountered
            break
        for x in range(0,len(repos['items'])):
            search_user_list.append(repos['items'][x]['login'])
    print search_user_list


def get_org_repos():
    URL = "https://api.github.com/orgs/"+args.orgname+"/"+"repos?type=all"+"&page="
    page = 1
    while True:
        full_url = URL+str(page)
        page +=1
        req = requests.get(full_url, headers=Headers)
        repos = json.loads(req.text)
        if len(repos) == 0:
            break
        for repo in repos:
            org_repo.append(repo['full_name'])
    print org_repo


def collab_user():
    for repo in org_repo:
        print repo
        try:
            URL = "https://api.github.com/repos/"+repo+"/contributors"
            print URL
            req = requests.get(URL, headers=Headers)
            repos = json.loads(req.text)
            for repo in repos:
                print repo['login']
                collab_list.append(repo['login'])
        except Exception as e:
            print e
    print list(set(collab_list))


def user_repo():
    for repo1 in org_mem_list:
        URL = "https://api.github.com/users/"+repo1+"/"+"repos?type=all"+"&page="
        page = 1
        while True:
            full_url = URL+str(page)
            print full_url
            page +=1
            try:
                req = requests.get(full_url, headers=Headers)
                repos = json.loads(req.text)
                if len(repos) == 0:
                    break
                for repo in repos:
                    user_repo_list.append(repo['full_name'])
            except Exception as e:
                print e
    print user_repo_list
#    for repo1 in collab_list:
#        URL = "https://api.github.com/users/"+repo1+"/"+"repos?type=all"+"&page="
#        page = 1
#        while True:
#            full_url = URL+str(page)
#            print full_url
#            page +=1
#            try:
#                req = requests.get(full_url, headers=Headers)
#                repos = json.loads(req.text)
#                if len(repos) == 0:
#                    break
#                for repo in repos:
#                    user_repo_list.append(repo['full_name'])
#            except Exception as e:
#                print e


    for repo1 in search_user_list:
        URL = "https://api.github.com/users/"+repo1+"/"+"repos?type=all"+"&page="
        page = 1
        while True:
            full_url = URL+str(page)
            print full_url
            page +=1
            try:
                req = requests.get(full_url, headers=Headers)
                #print req.text
                repos = json.loads(req.text)
                if len(repos) == 0:
                    break
                for repo in repos:
                    user_repo_list.append(repo['full_name'])
            except Exception as e:
                print e

    print "Unique repo list"
    print list(set(user_repo_list))


def secret_scan_in_user_repo():
    with open('githubtestdork.txt') as f:
        for i in f:
            url_list = list()
            for item in range(0,100):
                URL = "https://api.github.com/search/code?q={}+repo:{}&page=".format(i.strip(),user_repo_list[item])
                page = 1
                while True:
                    full_url = URL + str(page)
                    page +=1
                    try:
                        req = requests.get(full_url, headers=Headers)
                        repos = json.loads(req.text)
                    except Exception as e:
                        print e

                    if (("items" in repos and str(repos['items']) == '[]') or ("message" in repos and str(repos["message"]) == "Not Found")):#  or (str(repos["documentation_url"] == "https://developer.github.com/v3/search/"))):
                        break
                    elif ("documentation_url" in repos and str(repos["documentation_url"] == "https://developer.github.com/v3/#rate-limiting")):
                        URL = "https://api.github.com/rate_limit"
                        req = requests.get(URL, headers=Headers)
                        repos1 = json.loads(req.text)
                        reset_time = repos1['resources']['search']['reset']
                        current_time = int(time.time())
                        sleep_time = reset_time - current_time + 1
                        print "Sleeping for some time"
                        time.sleep(abs(sleep_time))
                    else:
                        for x in range(0,len(repos['items'])):
                            s = i.strip()
                            vul_item = s + "." + user_repo_list[item]
                            url_dict[vul_item]=repos['items'][x]['html_url']
                            url_list.append(repos['items'][x]['html_url'])

    print url_dict


def secret_scan_in_org_repo():
    with open('githubtestdork.txt') as f:
        for i in f:
            url_list = list()
            for item in range(0,100):
                URL = "https://api.github.com/search/code?q={}+repo:{}&page=".format(i.strip(),org_repo[item])
                page = 1
                while True:
                    full_url = URL + str(page)
                    page +=1
                    try:
                        req = requests.get(full_url, headers=Headers)
                        repos = json.loads(req.text)
                    except Exception as e:
                        print e

                    if (("items" in repos and str(repos['items']) == '[]') or ("message" in repos and str(repos["message"]) == "Not Found")):#  or (str(repos["documentation_url"] == "https://developer.github.com/v3/search/"))):
                        break
                    elif ("documentation_url" in repos and str(repos["documentation_url"] == "https://developer.github.com/v3/#rate-limiting")):
                        URL = "https://api.github.com/rate_limit"
                        req = requests.get(URL, headers=Headers)
                        repos1 = json.loads(req.text)
                        reset_time = repos1['resources']['search']['reset']
                        current_time = int(time.time())
                        sleep_time = reset_time - current_time + 1
                        print "Sleeping for some time"
                        time.sleep(abs(sleep_time))
                    else:
                        for x in range(0,len(repos['items'])):
                            s = i.strip()
                            vul_item = s + "." + org_repo[item]
                            url_dict[vul_item]=repos['items'][x]['html_url']
                            url_list.append(repos['items'][x]['html_url'])

    print url_dict


if __name__ == '__main__':
    #test()
    #t1 = threading.Thread(target=member_list, name='t1')
    #t2 = threading.Thread(target=search_user, name='t2')
    t3 = threading.Thread(target=get_org_repos, name='t3')
    #t4 = threading.Thread(target=user_repo, name='t4')
    t5 = threading.Thread(target=secret_scan_in_org_repo, name='t4')
    #t6 = threading.Thread(target=secret_scan_in_user_repo, name='t6')
    t3.start()
    #t1.start()
    t3.join()
    t5.start()
    #t4.join()
    #t6.start()
    #t1.join()
    #t4.start()