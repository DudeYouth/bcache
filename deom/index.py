#coding=utf-8
import os
import hashlib
import sys
import re
import time
import json

# 获取目录下的所有html文件
def getHtmlFile(path):
    ret = []
    reg = r'.*?\.(html|htm)'
    for root, dirs, files in os.walk(path):  
        for filespath in files: 
            filename = os.path.join(root,filespath).strip()
            result = re.match(reg,filename)
            if result:
                ret.append(os.path.abspath(result.group()))

    return ret;

# 生成文件的hash值
def createFileHash(filepath):
    hash = ''
    try:
        filehandle = open(filepath,'rb')
        with filehandle as f:
            md5obj = hashlib.md5()
            md5obj.update(f.read()+filepath)
            hash = md5obj.hexdigest()
            filehandle.close()
    finally:
        return hash

# 获取html文件里面的链接
def getLink(path):
    reg = r'(src|href)=[\'\"](.+?\.(js|css).*?)[\'\"]'
    filehandle = open(path,'r')
    result = []
    try:
        text = filehandle.read()
        result = re.findall(reg,text)
        filehandle.close()
    finally:
        filehandle.close()
        links = []
    links = []
    if len(result):
        for value in result:
            links.append({"source":value[1],"absolute":joinSrc(os.path.dirname(path),value[1].split('?')[0])})
    return links

# 替换版本号
def replaceVersion(filename,links):
    filehandle = open(filename,'r+')
    content = filehandle.read()
    for link in links:
        l = link.split('?')
        strs = ''
        if len(l)>1:
            strs = l[1]
            if strs[0:2]=='v=':
                arr = strs.split('&')
                arr.pop(0)
                if len(arr)>1:
                    strs = '&'.join(arr)
                elif len(arr)==1:
                    strs = arr[0]
                else:
                    strs = ''
        param = '?v=' + str(int(time.time()))
        if strs:
            param = param + '&' + strs
        content = content.replace(link,l[0] + param )
    
    filehandle.close()
    filehandle = open(filename,'w')
    filehandle.write(content)

# 分割路径     
def splitSrc(path):
    path = path.replace("\\", "/")
    arr = path.split('/') 
    return arr

# 拼接路径
def joinSrc(path1,path2):
    arr1 = splitSrc(path1)
    arr2 = splitSrc(path2)
    arr3 = arr2[:]
    for value in arr2:
        if value=='.':
            arr3.pop(1)
        if value=='..':
            arr1.pop()
            arr3.pop(0)
    return '/'.join(arr1)+'/'+'/'.join(arr3)

# 删除过期的hash
def deleteHash(data,key,value):
    newdata = []
    for k in data.keys():
        print(data[k][key],value)
        if data[k][key]==value:
            del data[k]
            return data
    return data

if __name__ == "__main__":
    print('start...')
    files = getHtmlFile('./')
    cacheName = 'cache'
    if not os.path.isfile(cacheName):
        filehandle = open(cacheName,'w+')
        filehandle.close()
    caches = {}
    flag = False
    try:
        filehandle = open(cacheName,'r+')
        text = filehandle.read()
        filehandle.close()
        if len(text):
            caches = json.loads(text)
    finally:
        print('get cache is ok...')
    
    for filename in files:
        links = getLink(filename)
        changeLinks = []
        for link in links:
            hash = createFileHash(link['absolute'])
            if hash=='':
                print(link['absolute'] + ' is not exists! Error in ' + filename)
            if caches.has_key(hash) or hash=='':
                continue
            else:
                changeLinks.append(link['source'])
                print('Change file : '+link['absolute'])
                caches = deleteHash(caches,'absolute',link['absolute'])
                caches[hash] = link
        if len(changeLinks)>0:
            replaceVersion(filename,changeLinks)
            flag = True
    print('change complete')
    if flag:
        filehandle = open(cacheName,'w')
        filehandle.write(json.dumps(caches))
        filehandle.close()
    
