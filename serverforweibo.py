import requests
import json
import os
import traceback

#TODO
# 要把时间戳写到config里去
def gettarget():
    filepath=os.path.split(os.path.realpath(__file__))[0]+os.sep+'target.txt'
    with open(filepath,'rb') as f:
        #这里splitlines之后没有换行符
        lines=f.read().splitlines()
        lines=[line.decode('utf-8-sig').split() for line in lines ]
    return lines
def getdata(targetid,targetname,sincetime):
    base_url = 'https://m.weibo.cn/api/container/getIndex?containerid=107603'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0'}
    html=requests.get(base_url+targetid,headers=headers)
    flag=1
    getid=0
    is_top=0
    weiboinfo=[]
    #时间戳的判断,since_id,每次修改微博的内容，时间戳都会改变
    #这里要修正一下，since_id是用来分页的，也就是说没有产生新的页数，since_id不会改变
    #新策略是用mblog里面的id来判断是否值最新的微博
    jsons=html.json()
    #since_id=jsons['data']['cardlistInfo']['since_id']
    try:
        is_top=jsons['data']['cards'][0]['mblog']['isTop']
    except:
        print('NO pinned weibo')
    if is_top:
        getid = 1
    # 如果是转发，获取转发的内容
    newest = jsons['data']['cards'][getid]
    text = newest['mblog']['text']
    # print(text)
    weiboinfo.append(text)
    try:
        if newest['mblog']['retweeted_status']:
            weiboinfo.append(newest['mblog']['retweeted_status']['text'])
    except:
        pass
    #时间的获取：
    lastime=jsons['data']['cards'][getid]['mblog']['id']
    if str(lastime)==str(sincetime):
        flag=0
    return flag,targetname,weiboinfo,lastime
def update_target_config(date):
    filepath = os.path.split(os.path.realpath(__file__))[0] + os.sep + 'target.txt'
    with open(filepath, 'rb') as f:
        # 这里splitlines之后没有换行符
        lines = f.read().splitlines()
        lines = [line.decode('utf-8-sig').split() for line in lines]
        output=[]
        for line,newestime in zip(lines,date):
            line[2]=str(newestime)
            updatinfo=' '.join(line)
            output.append(updatinfo)
    with open(filepath,'w',encoding='utf-8') as f:
        f.write('\n'.join(output))

def senddata(flag,targetname,info):
    if flag:
        base_url='https://sc.ftqq.com/SCU104985T08285d2851087b34878ed32f7dd933745f06be1f29d36.send'
        params={'text':targetname,'desp':''.join(info)}
        requests.get(base_url,params=params)


def main():
    lines=gettarget()
    date=[]
    for line in lines:
        data=getdata(*line)
        date.append(data[-1])
        senddata(*data[:3])
    update_target_config(date)

if __name__ == '__main__':
    main()