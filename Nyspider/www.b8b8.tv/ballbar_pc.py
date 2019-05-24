import requests
from bs4 import BeautifulSoup
import pymysql
import json
import time
import re

def load_mysql_setting():
    f=open('./mysql_setting.json','r',encoding='utf8')
    data=json.load(f)
    return data

def insert_into_mysql(result):
    userdata=load_mysql_setting()
    conn=pymysql.connect(host=userdata['host'],user=userdata['user'],passwd=userdata['passwd'],db=userdata['db'],port=userdata['port'],charset=userdata['charset'])
    cur=conn.cursor()
    where_keys=['bmatch','bmain','bumain','btime']
    update_keys=['buse', 'btype', 'bsrc','bstart','batt','bdateline']
    for item in result:
        where_cmd=''
        for key in where_keys:
            try:
                where_cmd+=key+'='+'"%s"'%item[key]+' and '
            except:
                continue
        update_cmd=''
        for key in update_keys:
            try:
                update_cmd+=key+'='+'"%s"'%item[key]+','
            except:
                continue
        row=cur.execute('update chat_direct set %s where %s'%(update_cmd[:-1],where_cmd[:-4]))
        if row ==0:
            line=[]
            for key in ['bmatch','bmain','bumain','btime','buse', 'btype', 'bsrc','bstart','batt','bdateline']:
                try:
                    line.append(item[key])
                except:
                    line.append('')
            cur.execute('insert into chat_direct(bmatch,bmain,bumain,btime,buse,btype,bsrc,bstart,batt,bdateline) values'+str(tuple(line)))
    conn.commit()
    cur.close()
    conn.close()

def crawl_from_web():
    headers = {
        'Host':"www.b8b8.tv",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0"}
    html=requests.get('https://www.b8b8.tv',headers=headers,timeout=30).text.encode('ISO-8859-1').decode('utf8')
    table=BeautifulSoup(html,'lxml').find('div',id='rightbox').find_all('div',id='righteventbox')[1].find_all('li')
    result=[]
    timenow=time.strftime('%Y-%m-%d %H:%M:%S')
    nowtime=int(time.strftime('%H%M'))
    for li in table:
        try:
            spans=li.find_all('span')
            try:
                btype=spans[1].get_text()
            except:
                continue
            if btype not in ['篮球','足球']:
                continue
            if btype=='篮球':
                btype=1
            if btype=='足球':
                btype=2
            item={}
            item['bdateline']=timenow
            item['btype']=btype
            item['batt']=1
            item['btime']=spans[0].get_text()
            btime=int(item['btime'].replace(':',''))-5
            item['bmatch']=spans[2].get_text()
            name=spans[3].get_text().replace('\r','').replace('\n','').replace(' ','').replace('[HD]','')
            item['bmain']=name.split('VS')[0]
            item['bumain']=name.split('VS')[-1]
            if nowtime<btime:
                item['buse']=2
                item['bstart']=2
                result.append(item)
                continue
            item['bstart']=1
            videoid=li.find('script').get_text()
            videoid=re.findall("goliveurl\('(.*?)',",videoid)[0]
            bsrc=get_web_src(videoid)
            if bsrc==False:
                item['buse']=2
                result.append(item)
                continue
            item['buse']=1
            item['bsrc']=bsrc
            item['batt']=1
            result.append(item)
        except:
            continue
    return result

def get_web_src(videoid):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0"}
    try:
        html=requests.get('https://live2.ballbar.cc/watch/getdata.php?k='+videoid,headers=headers,timeout=20).text
    except:
        try:
            html=requests.get('https://live.ballbar.cc/watch/getdata.php?k='+videoid,headers=headers,timeout=20).text
        except:
            return False
    if 'box' not in html:
        return False
    url=html.split('$$$')[-1]
    return url

while True:
    f=open('log','a',encoding='utf8')
    try:
        result=crawl_from_web()
    except:
        timenow=time.strftime('%Y-%m-%d %H:%M:%S')
        f.write(timenow+'\t抓取失败\r\n')
        time.sleep(2)
        continue
    try:
        insert_into_mysql(result)
    except:
        timenow=time.strftime('%Y-%m-%d %H:%M:%S')
        f.write(timenow+'\t插入数据库失败\r\n')
        time.sleep(10)
        continue
    timenow=time.strftime('%Y-%m-%d %H:%M:%S')
    print(timenow,'ok')
    f.write(timenow+'\tok\r\n')
    time.sleep(20)
