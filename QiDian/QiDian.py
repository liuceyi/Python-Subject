#!/usr/bin/env python3
# coding=utf-8
# author:sakuyo
#----------------------------------
import requests,sys,os
from bs4 import BeautifulSoup

class downloader(object):
    def __init__(self,target):#初始化
        self.target = target
        self.bookTitle = ''
        self.chapterNames = []
        self.chapterHrefs = []
        self.chapterNum = 0
        self.session = requests.Session()
    def GetChapterInfo(self):#获取章节名称和链接
        req = self.session.get(url=self.target)
        req.raise_for_status()
        req.encoding = req.apparent_encoding
        html = req.text
        bf = BeautifulSoup(html,"html.parser")
        self.bookTitle = bf.find('div',class_='book-info').find('h1').find('em').string
        catalogDiv = bf.find('div',class_='catalog-content-wrap',id='j-catalogWrap')
        volumeWrapDiv = catalogDiv.find('div',class_='volume-wrap')
        volumeDivs = volumeWrapDiv.find_all('div',class_='volume')

        for volumeDiv in volumeDivs:
            aList = volumeDiv.find_all('a')
            for a in aList:
                chapterName = a.string
                chapterHref = a.get('href')
                self.chapterNames.append(chapterName)
                self.chapterHrefs.append('https:'+chapterHref)
            self.chapterNum += len(aList)
    def GetChapterContent(self,chapterHref):#获取章节内容
        req = self.session.get(url=chapterHref)
        req.raise_for_status()
        req.encoding = req.apparent_encoding
        html = req.text
        bf = BeautifulSoup(html,"html.parser")
        mainTextWrapDiv = bf.find('div',class_='main-text-wrap')
        readContentDiv = mainTextWrapDiv.find('div',class_='read-content j_readContent')
        readContent = readContentDiv.find_all('span',class_='content-wrap')
        if readContent == []:
            textContent = readContentDiv.text.replace('<p>','\r\n')
            textContent = textContent.replace('</p>','')
        else:
            for content in readContent:
                if content.string == '':
                    print('error format')
                else:
                    textContent += content.string + '\r\n'
        return textContent
    def GetBookInfo(self):
        return self.bookTitle
    def writer(self, path, name='', content=''):#存入txt
        with open(path, 'a', encoding='utf-8') as f: #a模式意为向同名文件尾增加文本
            if name == None:
                name=''
            if content == None:
                content = ''
            f.write(name + '\r\n')
            f.writelines(content)
            f.write('\r\n')

if __name__ == '__main__':#执行层
    target = 'https://book.qidian.com/info/1024995653#Catalog'
    dlObj = downloader(target)
    dlObj.GetChapterInfo()
    isContinue = input('即将下载：'+dlObj.GetBookInfo()+'，是否确认？(y/n)')
    if isContinue == 'y':
        bookTitle = dlObj.GetBookInfo()
    else:
        sys.exit(0)
    print('开始下载：')
    for i in range(dlObj.chapterNum):
        try:
            dlObj.writer( bookTitle+'.txt',dlObj.chapterNames[i], dlObj.GetChapterContent(dlObj.chapterHrefs[i]))
        except Exception:
            print('下载出错，已跳过'+str(Exception))
            pass
        sys.stdout.write("  已下载:%.2f%%" %  float(100*i/dlObj.chapterNum) + '\r')
        sys.stdout.flush()
    print('下载完成')
    



    

