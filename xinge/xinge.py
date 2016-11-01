#%%
import requests
import time
from PIL import Image
from bs4 import BeautifulSoup


url='http://s.crpa.net.cn/mlogin.aspx'
session=requests.session()
r=session.get(url)
r_soup=BeautifulSoup(r.text,'lxml')
image_src="http://s.crpa.net.cn/mlogin_img.aspx"
with open('captcha.jpg','wb') as f:
    image=session.get(image_src)
    f.write(image.content)
im=Image.open('captcha.jpg')
im.show()
im.close()


captcha=input('Input captcha:')

time1=time.time()

postdata={'txtCheckCode':captcha,
           '__VIEWSTATE':'/wEPDwULLTEwMjY5MTUwNjUPZBYCAgMPZBYCAgUPDxYCHgRUZXh0BT88Zm9udCBjb2xvcj1yZWQ+PGI+6aqM6K+B56CB6ZSZ6K+v77yM6K+36YeN5paw6L6T5YWlPC9iPjwvZm9udD5kZBgBBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WAQUHQnV0dG9uMYBe0FqCcPn688UB66TnPvtxo6OHlKm7EVl0hdmhthmr',
          '__VIEWSTATEGENERATOR':'B0A1EB3C',
          '__EVENTVALIDATION':'/wEdAAN7D5zsBAYwF/2Wq2SIW07w9XU/Y71901ANuAMxuQ5LR834O/GfAV4V4n0wgFZHr3esyZ0J9yUimm9oMnpxn3z4pNmhFdJUWiaVhLVtCU0q4w==',
          'Button1.x':'0','Button1.y':'0'
          }

headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Host':'s.crpa.net.cn'}
session.post('http://s.crpa.net.cn/mlogin.aspx',headers=headers,data=postdata,allow_redirects=True)

month='201610'
month_url='http://s.crpa.net.cn/default.aspx?month='+month
r=session.get(month_url)

r_soup=BeautifulSoup(r.text,'lxml')
#print(r_soup.get_text())
#with open('source.txt','w') as f:
#    f.write(r_soup.prettify())
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

#for i,e in enumerate(entries):
#    print(i,e)

#%%
def crawl(entry):
    has_entry=False
    name,entry_url=entry
    req=session.get(entry_url)
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
                next_page_resp=session.get(next_page_url)
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
for entry in entries:
    crawl(entry)

print('Elapsed time:',time.time()-time1)