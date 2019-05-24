import requests
import json

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.5",
    'Host':'sysjk.ivdc.org.cn:8081',
    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0"}

def table_page(page):
    data={
    'start':page*20,
    'limit':20,
    'condList':'',
    }
    html=requests.post('http://sysjk.ivdc.org.cn:8081/cx/queryjksyzcxx/queryJksyzcxx.do', data=data,headers=headers).text
    data=json.loads(html)['rows']
    result=[]
    keys=['scqymc', 'gg', 'byx', 'bz', 'yxqks', 'scqyywmc', 'yxqjz', 'syywmc', 'zsh', 'sccmc', 'shr', 'shrq', 'syz', 'symc', 'ggrq', 'ggh', 'itemid', 'sccdz', 'yxqx']
    for item in data:
        '''
        for key in item:
            keys.append(key)
        print(keys)
        return
        '''
        line=[]
        for key in keys:
            try:
                line.append(item[key])
            except:
                line.append('')
        result.append(line)
    return result

def main():
    page=0
    while True:
        result=table_page(page)
        if result==[]:
            break
        f=open('data/9_jksy.txt','a',encoding='utf-8')
        for line in result:
            f.write(str(line)+'\n')
        f.close()
        print(page,'ok')
        page+=1

main()
