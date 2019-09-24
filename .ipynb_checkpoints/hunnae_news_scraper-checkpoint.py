#!/usr/bin/env python
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup
from IPython.display import clear_output
from datetime import date, datetime, timedelta
import glob, requests, urllib.request, urllib.parse, csv, re, time, os, numpy as np, pandas as pd


# In[2]:


def daum_url(start, end, query, press_name) :
    press_id_lists = {'경향신문':'16bfGN9mQcFhOx4F5l',
                  '한겨레':'16CIYSC5zGTVsMKcxM',
                  '조선일보':'16EeZKAuilXKH5dzIt',
                  '중앙일보':'16nfco03BTHhdjCcTS',
                  '동아일보':'16Et2OLVVtHab8gcjE',
                  '국민일보':'16NwX_ox536G_zyJUF',
                  '한국일보':'16hsvX4VEJdcIZzt_z',
                  '한국경제':'16qCuwnoTf8fLmrhD1',
                  '매일경제':'16jCK_TdtzwnmXfznB'}
    pre_url = "https://search.daum.net/search?w=news&sort=recency&q=%s&cluster=n&s=NS&a=STCF&dc=STC&pg=1&r=1&p=%d&rc=1&at=more&sd=%d000000&ed=%d235959&period=u&cp=%s&cpname=%s"
    url = pre_url %(urllib.parse.quote(query),
                    1,
                    start,
                    end,
                    press_id_lists[str(press_name)],
                    urllib.parse.quote(press_name))
    return(url)


# In[3]:


def daum_url_pagenum(start, end, query, press_name, page_num) :
    press_id_lists = {'경향신문':'16bfGN9mQcFhOx4F5l',
                  '한겨레':'16CIYSC5zGTVsMKcxM',
                  '조선일보':'16EeZKAuilXKH5dzIt',
                  '중앙일보':'16nfco03BTHhdjCcTS',
                  '동아일보':'16Et2OLVVtHab8gcjE',
                  '국민일보':'16NwX_ox536G_zyJUF',
                  '한국일보':'16hsvX4VEJdcIZzt_z',
                  '한국경제':'16qCuwnoTf8fLmrhD1',
                  '매일경제':'16jCK_TdtzwnmXfznB'}
    pre_url = "https://search.daum.net/search?w=news&sort=recency&q=%s&cluster=n&s=NS&a=STCF&dc=STC&pg=1&r=1&p=%d&rc=1&at=more&sd=%d000000&ed=%d235959&period=u&cp=%s&cpname=%s"
    url = pre_url %(urllib.parse.quote(query),
                    page_num,
                    start,
                    end,
                    press_id_lists[str(press_name)],
                    urllib.parse.quote(press_name))
    return(url)


# In[4]:


def daumlinknews_scraper(url) :
    basic_header = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)\AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
                    "Accept":"text/html,application/xhtml+xml,application/xml;\q=0.9,imgwebp,*/*;q=0.8"}
    soup = BeautifulSoup(requests.Session().get(url, headers=basic_header).text, 'html.parser')
    category = soup.find('h2', attrs={'id':'kakaoBody'}).text
    title = soup.find('h3', attrs={'class':'tit_view'}).text
    content = ' '.join(' '.join([each.text for each in soup.find_all(['p','div'], attrs={'dmcf-ptype':'general'})]).split())
    date = [each_info.text[3:13] for each_info in soup.find_all('span', attrs={'class':'txt_info'}) if '입력' in each_info.text][0]
    
    return title, date, content, category


# In[5]:


def press_scraper(url, press_name) :
    basic_header = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)\AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
          "Accept":"text/html,application/xhtml+xml,application/xml;\q=0.9,imgwebp,*/*;q=0.8"}

    if press_name == '한겨레' :
        soup = BeautifulSoup(requests.Session().get(url, headers=basic_header).text, 'lxml')
        title = soup.find('span', attrs={'class':'title'}).text
        date = '.'.join(re.findall(r'\d+',soup.find('p', attrs={'class':'date-time'}).span.text)[:3])
        precontent = soup.find('div', attrs={'class':'text'})
        for each in precontent.find_all(['div', 'div', 'p', 'b', 'font']) :
            each.decompose()
        content = ' '.join(precontent.text.split())
    
    elif press_name == '중앙일보' :
        soup = BeautifulSoup(requests.Session().get(url, headers=basic_header).text, 'lxml')
        title = soup.find('h1', attrs={'id':'article_title'}).text
        date = soup.find('div', attrs={'class':'byline'}).find_all('em')[1].text[3:][:10]
        precontent = soup.find('div', attrs={'id':'article_body'})
        for each in precontent.find_all(['div', 'img', 'p', 'b', 'font']) :
            each.decompose()
        content = ' '.join(precontent.text.split())
    
    elif press_name == '경향신문' :
        soup = BeautifulSoup(requests.Session().get(url, headers=basic_header).text, 'lxml')
        if soup.find('h1').text != '향이네' :
            title = soup.find('h1').text
            date = '.'.join(re.findall(r'\d+', soup.find('div', attrs={'class':'byline'}).find_all('em')[0].text)[:3])
            precontent = soup.find('div', attrs={'class':'art_cont'}).find_all('p', attrs={'class':'content_text'})
            for i in precontent :
                for j in i.find_all(['div', 'img', 'b', 'strong', 'font']) :
                    j.decompose()
            content = ' '.join([each.text for each in precontent if each.text!=''])
        else :
            title = soup.find('div', attrs={'class':'art_tit'}).text
            date = soup.find('span', attrs={'class':'date'}).text[:10]
            content = ' '.join([' '.join(each.text.split()) for each in soup.find_all('p', attrs={'class':'art_text'})])

    else : #'한국경제'
        soup = BeautifulSoup(requests.Session().get(url, headers=basic_header).text, 'lxml')
        title = soup.find('h1', attrs={'class':'title'}).text
        date = soup.find('span', attrs={'class':'date-published'}).span.text[:10]
        precontent = soup.find('div', attrs={'id':'articletxt'})
        for each in precontent.find_all(['div', 'img', 'b', 'strong', 'font']) :
            each.decompose()
        content = ' '.join(precontent.text.split())
    
    return title, date, content


# In[13]:


def hunnae_scraper(start, end, query, press_name) :
    if os.path.exists(str(start)+'_'+str(end)+'_'+query+'_'+press_name+'.txt') :
        os.remove(str(start)+'_'+str(end)+'_'+query+'_'+press_name+'.txt')
        
    news_links, title_list, date_list, content_list, query_list, press_list, category_list = ([] for i in range(7))
    date_list = [datetime.strptime(str(end),'%Y%m%d') - timedelta(days=x) 
             for x in range(0, (datetime.strptime(str(end),'%Y%m%d')-datetime.strptime(str(start),'%Y%m%d')).days+1)]
    session = requests.Session()
    header = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)\AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
              "Accept":"text/html,application/xhtml+xml,application/xml;\q=0.9,imgwebp,*/*;q=0.8"}
    url = daum_url(start, end, query, press_name)
    req = session.get(url, headers=header)
    soup = BeautifulSoup(req.text, 'html.parser')
    total_num_article = int(''.join(re.findall('\d+',re.search(r'/ (.*?)건',soup.find('span', attrs={'class':'txt_info'}).text).group(1))))
    
    try : #20190615 새로 추가한 것...
        if total_num_article <= 800 :
            for each in range(1,(total_num_article//10)+2) :
                new_soup = BeautifulSoup(session.get(daum_url_pagenum(start, end, query, press_name, each), headers=header).text, 'html.parser')
                for each_link in new_soup.find_all('div', attrs={'class':'wrap_tit mg_tit'}) :
                    news_links.append(each_link.a['href'][:-4])
                    query_list.append(query)
                    press_list.append(press_name)
                    try :
                        title, date, content, category = daumlinknews_scraper(each_link.a['href'][:-4])
                        with open(str(start)+'_'+str(end)+'_'+query+'_'+press_name+'.txt','a') as f :
                            f.writelines(each_link.a['href'][:-4]+'\n')
                    except :
                        title, date, content, category = [None for i in range(4)]
                        with open(str(start)+'_'+str(end)+'_'+query+'_'+press_name+'.txt','a') as f :
                            f.writelines('[ERROR] ' + each_link.a['href'][:-4] + '\n')
                    title_list.append(title)
                    date_list.append(date)
                    content_list.append(content)
                    category_list.append(category)
                    time.sleep(.25)
                    clear_output(wait=True)
                    print(len(news_links),'/',total_num_article)

        else :
            for each_date in date_list :
                time.sleep(.25)
                new_url = daum_url(int(each_date.strftime('%Y%m%d')), int(each_date.strftime('%Y%m%d')), query, press_name)
                new_req = session.get(new_url, headers=header)
                new_soup = BeautifulSoup(new_req.text, 'html.parser')
                num_article = int(''.join(re.findall('\d+',re.search(r'/ (.*?)건',new_soup.find('span', attrs={'class':'txt_info'}).text).group(1))))

                if num_article == 0 :
                    pass
                else :
                    for each_page in range(1,(num_article//10)+2) :
                        new_soup2 = BeautifulSoup(session.get(
                            daum_url_pagenum(int(each_date.strftime('%Y%m%d')), int(each_date.strftime('%Y%m%d')), query, press_name, each_page), headers=header).text, 'html.parser')
                        for each_link in new_soup2.find_all('div', attrs={'class':'wrap_tit mg_tit'}) :
                            news_links.append(each_link.a['href'][:-4])
                            query_list.append(query)
                            press_list.append(press_name)
                            try :
                                title, date, content, category = daumlinknews_scraper(each_link.a['href'][:-4])
                                with open(str(start)+'_'+str(end)+'_'+query+'_'+press_name+'.txt','a') as f :
                                    f.writelines(each_link.a['href'][:-4]+'\n')
                            except :
                                title, date, content, category = [None for i in range(4)]
                                with open(str(start)+'_'+str(end)+'_'+query+'_'+press_name+'.txt','a') as f :
                                    f.writelines('[ERROR] ' + each_link.a['href'][:-4] + '\n')
                            title_list.append(title)
                            date_list.append(date)
                            content_list.append(content)
                            category_list.append(category)
                            time.sleep(.25)
                            clear_output(wait=True)
                            print(len(news_links),'/',total_num_article)
    except :
        pass
    print(len(news_links),'/',total_num_article, 'COMPLETE!')
    pd.DataFrame(zip(news_links, query_list, press_list,
                     title_list, date_list, category_list, content_list),
             columns=['url', 'query', 'press', 'title', 'date', 'category', 'content']).to_csv(str(start)+'_'+str(end)+'_'+query+'_'+press_name+'.csv')