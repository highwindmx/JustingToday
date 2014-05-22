#!/usr/bin/env python3
# Copyright (C) 2014 highwind <highwindmx@126.com>
# Use of this source code is governed by GPLv3 license that 
# in http://www.gnu.org/licenses/gpl-3.0.html
# Filename: JustingToday.py
__version__  = 0.2

import os
import subprocess
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup as BS
from time import time,localtime,strftime
import queue
import threading

# 程序开始
# 赋值
Justing = {
        'TargetDir'   : os.path.expanduser('~/Music/JustingToday/'),
        'LogName'     : 'JustingToday.log',
        'DownloadNum' : 6,
        'UpdateNum'   : 18,
        'Homepage'    : 'http://www.justing.com.cn/index.jsp',
        'SelectRule'  : '#tabs-3 > p > a[target="_blank"]',
        'MP3Head'     : 'http://dl.justing.com.cn/page/{0}.mp3',
        'ShareFolder' : os.path.expanduser('~/Public/')
}

# 第一部分 从静雅思听首页地址解析出MP3文件的下载地址
def parse_page(pageUrl,selectRule,updateNum,mp3FileHead,targetDir,logName):
    print("Acquiring Your url: {0}".format(pageUrl))
    pageHtml = urllib.request.urlopen(pageUrl).read()

    print("Your url: {0} is acquird, parsing now".format(pageUrl))
    pageSoup = BS(pageHtml)
    pageSoupElem = pageSoup.select(selectRule)

    mp3FileUrl= list(range(updateNum))
    if os.path.exists(targetDir):
        print("Good ,the target path {0} is already there".format(targetDir))
    else:
        print("Sorry ,the target path {0} is not there, creating it for you".format(targetDir))
        os.makedirs(targetDir)
    logList = open(os.path.join(targetDir,logName),'w')
    for i in range(updateNum):
        mp3FileUrl[i] = mp3FileHead.format(pageSoupElem[i].text.strip('\xa0'))
        print(mp3FileUrl[i])
        logList.write("%s\n" % mp3FileUrl[i])
    logList.close()
    return
# 第一部分 结束

# 第二部分 队列下载
def make_DownloadFolder(targetDir):
    timePath = strftime("%Y-%m-%d_%H-%M-%S",localtime(time()))
    fullPath = os.path.join(targetDir,timePath)
    os.makedirs(fullPath)
    return fullPath

class download(threading.Thread):
    def __init__(self,que,toDir):
        threading.Thread.__init__(self)
        self.que=que
        self.todir=toDir
        return
    def run(self):
        while True:
            if not self.que.empty():
                #os.system("wget -c -P "+self.todir+" --restrict-file-names=nocontrol "+self.que.get())
                #os.system("axel -n6 -a -o "+self.todir+" "+self.que.get())
                #commands.getstatus("axel -n6 -a -o "+self.todir+" "+self.que.get())
                print(os.system("axel -n6 -a -o "+self.todir+" "+self.que.get()))
            else:
                break
        return

def startDown(logName,fullPath,targetDir,downloadNum):
    logListFile = open(os.path.join(targetDir,logName),"r",encoding="utf-8")
    que=queue.Queue()
    for lineItem in logListFile:
        downloadUrl = urllib.parse.quote(lineItem, safe=':/?=').strip('%0A')
        que.put(downloadUrl)
    for i in range(downloadNum):
        d=download(que,fullPath)
        d.start()
    logListFile.close()
    return

# 第二部分 结束

if __name__=='__main__':
    parse_page(
        Justing['Homepage'],Justing['SelectRule'],Justing['UpdateNum'],
        Justing['MP3Head'],Justing['TargetDir'],Justing['LogName']
           )

    Justing['FullPath'] = make_DownloadFolder(Justing['TargetDir'])
    startDown(Justing['LogName'],Justing['FullPath'],Justing['TargetDir'],Justing['DownloadNum'])

    # 如果用os.system则需要小心 xdg-open后面的空格哟
    subprocess.Popen(["xdg-open",Justing['FullPath']],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.Popen(["xdg-open",Justing['ShareFolder']],stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# 程序结束
