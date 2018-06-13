# -*- coding: UTF-8 -*-
from selenium import webdriver
import time
import SendKeys,os


def formaturl(urlelement):
    urlcul = urlelement.text.encode('utf-8')
    index = str(urlcul).find('›')
    urlstr = str(urlcul)
    if index > 0:
        urlstr = urlstr[0:index]
    urlstr = urlstr.rstrip()
    return urlstr

def wrap_urllist(urlvalues,urllist):
    url_index = urllist.__len__() + 1
    for urlelement in urlvalues:
        urlstr = str(url_index) + '.' + formaturl(urlelement)
        url_index += 1
        urllist.append(urlstr)
    return urllist

#write to file and prepare for new top 20
def write_to_file(fp,i,urlvalues):
    for urlvalue in urlvalues:
        urlcul = urlvalue.text.encode('utf-8')
        index = str(urlcul).find('›')
        urlstr = str(urlcul)
        if index > 0:
            urlstr = urlstr[0:index]
        urlstr = urlstr.rstrip()
        fp.write("{0}\n".format(urlstr))
        print "url {0} is {1}".format(i,urlstr)
        i = i + 1
    return fp

def prepare_filename():
    nowtime = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    nowtime = nowtime.replace(' ', 'T').replace('-', '').replace(':', '')
    # 获取当前文件数量，递增
    print 'os.getcwd()',os.getcwd()
    totalfiles = fileCountIn(os.getcwd())
    print 'total files:',totalfiles
    filename = str(totalfiles) + "test" + nowtime + ".txt"
    return filename

def fileCountIn(dir): return sum([len(files) for root,dirs,files in os.walk(dir)])

def get_dic_top20(file_lines,top20):
    newindex = 1
    for line in file_lines:
        key = newindex
        value = line.rstrip('\n')
        top20[key] = value
        newindex += 1

def getURLS_writetofile(searchkey):
    newtop20 = {}
    oldtop20 = {}
    urllist  = [] #get from webpage
    promotedURLs = [] #up urls
    downloadgradedURLs = [] #down urls
    keepasURLs = []
    outURLs = []
    newaddurls = []

    driver = webdriver.Chrome(os.getcwd()+'\chromedriver.exe')
    #driver=webdriver.Ie()
    driver.maximize_window()
    driver.get(r'https://www.google.com.hk/webhp?hl=zh-CN&sourceid=cnhp&gws_rd=ssl')
    driver.implicitly_wait(10)
    # e=driver.find_element_by_id("gs_lc0")
    key=driver.find_element_by_id("gs_lc0").find_element_by_tag_name('input')
    #如果页面加载失败
    trytime=0
    while key == None and trytime < 5:
        driver.refresh()
        time.sleep(5)
        trytime = trytime + 1

    key.send_keys(searchkey)
    time.sleep(10)
    # searchButton = driver.find_element_by_class_name('jsb').find_element_by_tag_name('input')
    # searchButton.click()

    SendKeys.SendKeys("{ENTER}")

    time.sleep(10)
    urlvalues = driver.find_elements_by_tag_name('cite')
    #create a folder if it's not existed
    if not os.path.exists('./googletop20'):
        os.mkdir('./googletop20')
    os.chdir('./googletop20')#切换到

    filename = prepare_filename()
    fp = open(filename,'w')#if file not exists, create a new one
    print 'today file:',fp.name
    i=1#the first page starts with 1 url
    fp = write_to_file(fp,i,urlvalues)
    urllist = wrap_urllist(urlvalues,urllist)#add to urllist to return to html
    #next page
    nextbutton = driver.find_element_by_xpath('//*[@id="pnnext"]/span[2]')
    nextbutton.click()
    time.sleep(5)
    urlvalues = driver.find_elements_by_tag_name('cite')

    i=11 #the 2nd page starts with 11 url
    fp = write_to_file(fp,i,urlvalues)
    urllist = wrap_urllist(urlvalues, urllist)
    print 'urllist:',urllist
    fp.close()
    driver.quit()

    totalFiles = fileCountIn(os.getcwd())
    if totalFiles > 1:
        #compare the two files
        files = os.listdir(os.getcwd())
        #find the new file and last time file
        for file in files:
            print 'file is:',file
            if file.startswith(str(totalFiles-1)):
                newfile = file
            if file.startswith(str(totalFiles-2)):
                oldfile = file

        #read the new one and last one
        fileslen = files.__len__()
        newresult = open(newfile,'r')
        oldresult = open(oldfile,'r')
        newlines = newresult.readlines()
        print 'newlines:',newlines
        oldlines = oldresult.readlines()
        print 'oldlines:',oldlines
        # oldindex = 1#start from 1
        # for oldline in oldlines:
        #     oldkey=oldindex
        #     oldvalue = oldline.rstrip('\n')
        #     oldtop20[oldkey]=oldvalue
        #     oldindex += 1
        # for newline in newlines:
        # newindex = 1
        # for newline in newlines:
        #     newkey = newindex
        #     newvalue = newline.rstrip('\n')
        #     newtop20[newkey]=newvalue
        #     newindex += 1
        get_dic_top20(oldlines, oldtop20)
        get_dic_top20(newlines, newtop20)

        #compare the two,get the comment:
        print 'oldtop20:',oldtop20
        print 'newtop20:',newtop20

        for oldindex in oldtop20.keys():
            oldurl = oldtop20[oldindex]
            if oldurl not in newtop20.values():
                outURLs.append(oldurl)
                pass
            if newtop20[oldindex] == oldurl:
                keepasURLs.append((oldurl, oldindex, oldindex))
            else:
                for newindex in newtop20.keys():
                    if newtop20[newindex] == oldurl:
                        if newindex > oldindex:
                            downloadgradedURLs.append((oldurl,oldindex,newindex))
                        elif newindex < oldindex:
                            promotedURLs.append((oldurl,oldindex,newindex))
        #if newurl is not existed in oldtop20, then it's new added
        for newindex in newtop20.keys():
            newurl = newtop20[newindex]
            if newurl not in oldtop20.values():
                newaddurls.append(newurl)

        print promotedURLs,'\n'
        print downloadgradedURLs,'\n'
        os.chdir(os.path.pardir)#back to up folder

    allurls = (urllist,promotedURLs,downloadgradedURLs,keepasURLs,newaddurls)
    print 'allurls:',allurls
    return allurls


if __name__ == '__main__':
    getURLS_writetofile(r'youtube downloader free')
    print 'final cwd:',os.getcwd()




