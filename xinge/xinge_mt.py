#%%
from threading import Thread
import requests
import random,time
from PIL import Image
from bs4 import BeautifulSoup

session=requests.session()
adapter = requests.adapters.HTTPAdapter(pool_connections=2000, pool_maxsize=2000)
session.mount('http://', adapter)

def test():
    count=0
    while True:
        rrr=session.get('http://s.crpa.net.cn/result_listN.aspx?id=20161031183235407')
        count+=1
        if count%20==0:
            print(count)
        index=rrr.text.find('请输入验证码登录')
        if index>0:
            return count 
def login(yundama=False):
    url='http://s.crpa.net.cn/mlogin.aspx'

    image_src="http://s.crpa.net.cn/mlogin_img.aspx"
    with open('captcha.jpg','wb') as f:
        image=session.get(image_src)
        f.write(image.content)
    
    
    if yundama==False:
        im=Image.open('captcha.jpg')
        im.show()
        im.close()
        captcha=input('Input captcha:')
    else:
        from yundama import YunDaMa
        ydm=YunDaMa('firearasi','icw4ever')
        cid,captcha=ydm.get_captcha(image.content,'captcha.jpg','image/jpeg')
        print('captcha recognized:',captcha)
    postdata={'txtCheckCode':captcha,
               '__VIEWSTATE':'/wEPDwULLTEwMjY5MTUwNjUPZBYCAgMPZBYCAgUPDxYCHgRUZXh0BT88Zm9udCBjb2xvcj1yZWQ+PGI+6aqM6K+B56CB6ZSZ6K+v77yM6K+36YeN5paw6L6T5YWlPC9iPjwvZm9udD5kZBgBBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WAQUHQnV0dG9uMYBe0FqCcPn688UB66TnPvtxo6OHlKm7EVl0hdmhthmr',
              '__VIEWSTATEGENERATOR':'B0A1EB3C',
              '__EVENTVALIDATION':'/wEdAAN7D5zsBAYwF/2Wq2SIW07w9XU/Y71901ANuAMxuQ5LR834O/GfAV4V4n0wgFZHr3esyZ0J9yUimm9oMnpxn3z4pNmhFdJUWiaVhLVtCU0q4w==',
              'Button1.x':'0','Button1.y':'0'
              }
    
    headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0',
            'Host':'s.crpa.net.cn'}
    session.post(url,headers=headers,data=postdata,allow_redirects=True)

def collect_entries(month='201610'):
    month_url='http://s.crpa.net.cn/default.aspx?month='+month
    r=session.get(month_url)
    
    r_soup=BeautifulSoup(r.text,'lxml')
    entries=[]
    cur_soup=r_soup
    while cur_soup is not None:
        tables=cur_soup.findAll('td',style='width:250px;')
        if len(tables)==0:
            tables=cur_soup.findAll('td',width='250')
        for i,t in enumerate(tables):
            a=t.find('a',target='_blank')
    
            href='http://s.crpa.net.cn/'+a.get('href')
            entries.append((a.get_text(),href))
        next_page=cur_soup.find('a',id='hylnext')
        if next_page is None:
            cur_soup=None
        else:
            next_page_url='http://s.crpa.net.cn/'+next_page.get('href')
            print(next_page_url)
            next_page_resp=session.get(next_page_url)
            print('nextpage')
            #print(next_page_resp.text)
            cur_soup=BeautifulSoup(next_page_resp.text,'lxml')
    return entries
#for i,e in enumerate(entries):
#    print(i,e)

#%%

def get_page(url,timeout=5):
    resp=session.get(url,timeout=timeout)
    if resp.text.find('请输入验证码登录')!=-1:
        login(yundama=True)
        resp=session.get(url,timeout=timeout)
    return resp

def crawl(entry):
    has_entry=False
    name,entry_url=entry
    req=get_page(entry_url)
    soup=BeautifulSoup(req.text,'lxml')
    table=soup.find('table',id='GridView1')
    if table is not None:
       output=[]
       while table is not None:
            rows=table.findAll('tr')
            #print('num rows',len(rows))
            if len(rows)>0:
                has_entry=True
                for row in rows:
                    cells=row.findAll('td')
                    strings=[c.get_text() for c in cells]
                    line=','.join(strings)
                    output.append(line)
            next_page=soup.find('a',id='hylnext')
            if next_page is None:
                table=None
            else:
                next_page_url='http://s.crpa.net.cn/'+next_page.get('href')
                print('next_page_url',next_page_url)
                next_page_resp=get_page(next_page_url)
                next_page_soup=BeautifulSoup(next_page_resp.text,'lxml')
                soup=next_page_soup
                table=next_page_soup.find('table',id='GridView1')
       if len(output)>0:
            filename=name.strip()+'.csv'
            filename=filename.replace('/','-')
            filename='tables/'+filename
            with open(filename,'w') as f:
                f.write('排名,卡号,鸽主,棚号,足环号,性别,羽色,眼砂,归巢时间,空距,分速,分赛')
                f.write('\n'.join(output))
    if has_entry:
        print(name)
    return has_entry
#%%

class CrawlThread(Thread):
    def __init__(self,entry_list):
        Thread.__init__(self)
        self.entry_list=entry_list
    def run(self):
        for entry in self.entry_list:
            crawl(entry)


if __name__=='__main__':
    login(yundama=True)
    time1=time.time()
    entries=collect_entries()
    random.shuffle(entries)
    length=len(entries)
    parts=10
    num_part=length//parts
    threads=[]
    for i in range(parts):
        entry_list=entries[i*num_part:min((i+1)*num_part,length)]
        thr=CrawlThread(entry_list)
        threads.append(thr)
        thr.start()
    for t in threads:
        t.join()
    print('Elapsed time:',time.time()-time1)