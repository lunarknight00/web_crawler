from bs4 import BeautifulSoup,Comment
import requests, re, csv,time,random


def fetchPage(url):
    page = requests.get(url)
    page.encoding ='utf-8'
    return BeautifulSoup(page.text, 'html.parser')


def cleanString(string) -> str:
    if re.search("（财富中文网）",string):
        return  string.replace("（财富中文网）",'')
    else:
        return string

def buildTextList(soup) -> tuple:
    Chinese, English = [], []
    for div in soup.findAll("div"):
        comment = div.find_all(string=lambda text: isinstance(text, Comment))
        if len(comment)==0:
            continue
        if re.search("cstart",comment[0]):
            Chinese += [strQ2B(cleanString(s.text)) for s in div.find_all("p") if re.search("译者",s.text) == None and re.search("审校",s.text) == None and len(s) != 0]
        if re.search("estart",comment[0]):
            English += [strQ2B(s.text) for s in div.find_all("p") if len(s) != 0]
    if len(Chinese) == len(English) and len(Chinese) == 0:
        return 0
    return Chinese,English

def strQ2B(ustring):
    pattern = re.compile('[，。：“”【】《》？；、（）‘’『』「」﹃﹄〔〕—·…]')
    fps = re.findall(pattern, ustring)

    if len(fps) > 0:
        ustring = ustring.replace('，', ',')
        ustring = ustring.replace('。', '.')
        ustring = ustring.replace('：', ':')
        ustring = ustring.replace('“', '"')
        ustring = ustring.replace('”', '"')
        ustring = ustring.replace('【', '[')
        ustring = ustring.replace('】', ']')
        ustring = ustring.replace('《', '<')
        ustring = ustring.replace('》', '>')
        ustring = ustring.replace('？', '?')
        ustring = ustring.replace('；', ':')
        ustring = ustring.replace('、', ',')
        ustring = ustring.replace('（', '(')
        ustring = ustring.replace('）', ')')
        ustring = ustring.replace('‘', "'")
        ustring = ustring.replace('’', "'")
#         ustring = ustring.replace('’', "'")
        ustring = ustring.replace('『', "[")
        ustring = ustring.replace('』', "]")
        ustring = ustring.replace('「', "[")
        ustring = ustring.replace('」', "]")
        ustring = ustring.replace('﹃', "[")
        ustring = ustring.replace('﹄', "]")
        ustring = ustring.replace('〔', "{")
        ustring = ustring.replace('〕', "}")
        ustring = ustring.replace('—', "-")
        ustring = ustring.replace('·', ".")
        ustring = ustring.replace('…',"...")
        
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 12288:                             
            inside_code = 32
        elif (inside_code >= 65281 and inside_code <= 65374): 
            inside_code -= 65248
        rstring += chr(inside_code)
    return rstring

def cleanCNText(sentences) -> list:
    
    for i in range(len(sentences)):
        if re.search("（财富中文网）",sentences[i]):
            sentences[i] = sentences[i].replace("（财富中文网）",'')
        if re.search("译者",sentences[i]):
            sentences[i] = []
        if re.search("审校",sentences[i]):
            sentences[i] = []
    return sentences

def getId(url):
    return re.findall(r"\d+",url)[-1]

def singleCrawler(url):
    data = fetchPage(url)
    filename = "fortune/fortune%s.csv"%getId(url)
    if not  buildTextList(data):
        print(f"{getId(url)} is not valid. So sad........")
        return
    # print(buildTextList(data))
    with open(filename,"w",newline='',encoding = "utf-8") as csvfile:
        fieldnames = ["Chinese","English"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
#         try:
        for CN, EN in list(zip(*buildTextList(data))):
            writer.writerow({"Chinese":CN ,"English":EN})
#         except:
#             return 0
    print("Crawl {}".format(getId(url))+" from fortune China is done")


if __name__ == "__main__":

# job continue at page 375

    base = "http://www.fortunechina.com/search/f500beta/searchArticle.do?facetAction=&facetStr=&curPage=1&sort=0&key="
    indeces = fetchPage(base)
    MAX_PAGE = int(max([re.findall(r'\d+',s.get("onclick"))[0] for s in indeces.find_all("a") if s.get("onclick") and re.search("Page",s.get("onclick"))]))

    # iterate all pages in the search base url
    

    # 
    #  change page from 1558 to MAX
    # 
    for i in range(1558 ,MAX_PAGE +1 ):
        urls = list()
        indexUrl = "http://www.fortunechina.com/search/f500beta/searchArticle.do?facetAction=&facetStr=&curPage={}&sort=0&key=".format(str(i))
        curPage = fetchPage(indexUrl)
        # time.sleep(random.uniform(0,1))
        
        print("Current page is {}".format(i))
        
        for s in curPage.find_all("a"):
            try:
                if re.search("content",s.get('href')):
                    urls.append(s.get("href"))
            except:
                continue

        # print(urls)
        print(f"Collected all the pages from current page {i}")
        for url in urls:
            # time.sleep(random.uniform(3,5))
            singleCrawler(url)
        print(f"Web crawling finished in page{i}. Awesome!!!")

    print("Great! All jobs are done!")