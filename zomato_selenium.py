from selenium import webdriver
import re
import pandas as pd
import sys
from bs4 import BeautifulSoup as bs
import requests
#create a new Firefox session in chrome using chromedriver 
req = webdriver.Chrome(executable_path='C:/selenium/chromedriver')#must be the chromedriver in this specified folder 
city=input("please enter city :")
list_of_url=[]#empty list
data=[]#empty list
def gather_num_pages():#gather information of number of pages 
    try:
        #get the pages of McDonalds Restaurant in provided city
        req.get("https://www.zomato.com/"+city+"/restaurants/mcdonalds")
        #Selenium hands the page source to Beautiful Soup
        hparse=bs(req.page_source, 'lxml')
        #to find the number of pages search contains
        page_num=hparse.find_all("div",{"class":"col-l-4 mtop pagination-number"})[0].text
        return [str(i) for i in range(1,int(re.findall('([0-9]+)', page_num)[-1])+1)]
        #exception call if network problem OR not avilability of McDonalds in the city OR entered city is not root city(mumbai is a root city of thane)
    except Exception:
        req.close()
        sys.exit("************"+city+" is not a root city or here no McDonalds Restaurant***********")
        
    
    

def gather_list_url():#gather list of all URL links 
    pages = gather_num_pages()
    list_of_url=[]#empty list
    #procedure to retrive all link in list
    print("\nNETWORK PROCESS:",end=" |")
    for j in pages:
        print("************|",end="")
        #one by one page request sent and retrive the raw data
        req.get("https://www.zomato.com/"+city+"/restaurants/mcdonalds?page="+str(j))
        #Beautiful Soup finds the link of zomato page
        hparse=bs(req.page_source, 'lxml')
        #get the all links
        all_url=hparse.find_all("div",{"class":"col-s-6 col-m-4"})
        #get all LIST of URL link in list into l
        for i in all_url:
            list_of_url.append(i.div.a["href"])#store link one by one in list_of_url
    return list_of_url

def fetch_detail():#fetch the require detail into DataFrame
    j=0
    list_of_url = gather_list_url()#get all the url into list_of_url
    print("\nDATA PROCESSING:",end=" ")
    for i in list_of_url:#iterate the list of URL
        df={}
        j+=1
        print("*",end="")
        req.get(i)
        #Selenium hands the page source to Beautiful Soup and get all details
        hparse=bs(req.page_source, 'lxml')
        #Beautiful Soup finds all the all details require
        c=hparse.find_all("div",{"class":"res-main-phone p-relative phone-details clearfix"})[0]
        #get data into DataFrame data values Name,Phone,Address,first reviewers Name,first Reviewers Score,Review Text and page link
        df["Name"]=str(re.findall('(.*?),', c["title"])).strip('[]')
        df["Phone"]=str(re.findall('([+][0-9]+)', c.text.strip())).strip('[]')
        df["Address"]=hparse.find_all("div",{"class":"borderless res-main-address"})[0].text.strip()
        df["Reviewers Name"]=hparse.find_all("div",{"class":"header nowrap ui left"})[0].text.strip()
        df["Reviewers Score"]=hparse.find_all("div",{"class":"rev-text mbot0 "})[0].div["aria-label"]
        df["Review Text"]=hparse.find_all("div",{"class":"rev-text mbot0 "})[0].text.strip()[39:]
        df["Link"]=i
        #append dataframe to data list
        data.append(df)
    return data  



def data_to_csv():#data store into csv process
    fetch_detail()
    df1=pd.DataFrame(data)
    #covert dataframe to CSV
    df1.to_csv("zomato_"+city+".csv",index=False)
    #Reading dat from CSV
   
data_to_csv()
req.close()
#read csv file
csv_file=pd.read_csv("zomato_"+city+".csv") 
csv_file
