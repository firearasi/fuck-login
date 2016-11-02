#%%
from threading import Thread
import requests
import random,time
from PIL import Image
from bs4 import BeautifulSoup


def login(yundama=False):
    session=requests.session()
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
    return session

def collect_entries(session,month='201610'):
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

def get_page(session,url,sleep=1):
    sess=session
    resp=sess.get(url)
    if(sleep>0):
        time.sleep(sleep)
    if resp.text.find('您的访问太频繁')!=-1 or resp.text.find('验证码')!=-1:
        #print('sleeping for url:',url)
        #time.sleep(600)
        #resp=session.get(url)
        sess=login(True)
        resp=sess.get(url)
    return sess,resp

def crawl(session,entry):
    has_entry=False
    name,entry_url=entry
    sess,req=get_page(session,entry_url)
    soup=BeautifulSoup(req.text,'lxml')
    
    try:
        num_records=soup.find('span',{'id':'FormView1_home_numLabel'}).get_text()
        print(entry)
        print(num_records)
    except AttributeError as e:
        print('NoneType in ', entry_url)
        return
    
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
                sess,next_page_resp=get_page(sess,next_page_url)
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
    return sess
    
    
#%%

class CrawlThread(Thread):
    def __init__(self,entry_list,session=None):
        Thread.__init__(self)
        self.entry_list=entry_list
        self.session=session or login(yundama=True)
    def run(self):
        for entry in self.entry_list:
            self.session=crawl(self.session,entry)


if __name__=='__main__':
    session=login(yundama=True)
    time1=time.time()
    entries=collect_entries(session, month='201610')
    random.shuffle(entries)
    length=len(entries)
    parts=1 #线程数
    num_part=length//parts
    threads=[]
    for i in range(parts):
        entry_list=entries[i*num_part:min((i+1)*num_part,length)]
        thr=CrawlThread(entry_list,session)
        threads.append(thr)
        thr.start()
    for t in threads:
        t.join()
    print('Elapsed time:',time.time()-time1)