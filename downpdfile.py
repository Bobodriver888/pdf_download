import requests
import json
import os
from PIL import Image
import time
import execjs
import time
import urllib3
import hashlib

urllib3.disable_warnings()
'''
只需要输入BOOKID
'''


'''配置数据'''
url='https://biz.bookln.cn/ebookpageservices/queryAllPageByEbookId.do'
imgpath=r'.\books\IMG\{}'
PDFPATH=r'.\books\PDF'
BOOKIDLIST=[24984]  ##只有该值需要手工输入，可以根据浏览器上url地址查看

'''
bookidlist=[24947,24948,24949,24950,24951,24952,24953,24954,28566,28567]
'''

headers = {
        'context-type': 'text/xml; charset=UTF-8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.17 Safari/537.36 Edg/81.0.416.12',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    }

data={
'ebookId': '',
'_timestamp': '',
'_nonce': '',
'_sign': ''
}

'''代码部分'''

def timestatic(func):
    def wrapper(*args, **kwargs):
        startTime = time.time()
        func(*args, **kwargs)
        endTime = time.time()
        msecs = (endTime - startTime)*1000
        if func.__name__=='get_page':
            print("下载电子书一页花费时间:%d ms" %msecs)
        else:
            print("合并电子书总共花费时间:%d ms" % msecs)
    return wrapper

@timestatic
def get_page(pagenum,url):
    #print('url=',url)
    onepage=requests.get(url=url,headers=headers,verify=False).content
    pagename=os.path.join(IMGPATH,str(pagenum)+'.jpeg')
    with open(pagename,'wb') as f:
        f.write(onepage)

@timestatic
def MergeImageToPdf(pdf_name):
    print('开始把图片合并为PDF文件...')
    file_list = os.listdir(IMGPATH)
    pic_name = []
    im_list = []
    for x in file_list:
        if "jpg" in x or 'png' in x or 'jpeg' in x:
            pic_name.append(x)

    pic_name.sort(key=lambda x: int(x.replace('.jpeg','')))
    print(pic_name)
    new_pic = []

    for x in pic_name:
        if "jpg" in x:
            new_pic.append(x)

    for x in pic_name:
        if "jpeg" in x:
            new_pic.append(x)

    print("hec", new_pic)

    os.chdir(IMGPATH)
    im1 = Image.open(new_pic[0])
    new_pic.pop(0)
    for i in new_pic:
        img = Image.open(i)
        # im_list.append(Image.open(i))
        if img.mode == "RGBA":
            img = img.convert('RGB')
            im_list.append(img)
        else:
            im_list.append(img)
    os.chdir('../../..')
    im1.save(pdf_name, "PDF", resolution=100.0, save_all=True, append_images=im_list)
    print("输出文件名称：", pdf_name)


def get_param(ebookId):
    _nonce = 'update_date:2020-0224___from:ithomia'
    _timestamp = int(time.time())
    sign_data = f'{_nonce}_nonce{_timestamp}_timestamp{ebookId}ebookId'
    _sign = hashlib.md5(sign_data.encode()).hexdigest().upper()
    return {'ebookId': ebookId,
            '_timestamp': _timestamp,
            '_nonce': _nonce,
            '_sign': _sign}


if __name__ == '__main__':
    for BOOKID in BOOKIDLIST:
        print('开始BOOKID={}的下载'.format(BOOKID))
        IMGPATH = imgpath.format(BOOKID)
        print(IMGPATH)
        if not os.path.exists(IMGPATH):
            os.makedirs(IMGPATH)
        if not os.path.exists(PDFPATH):
            os.makedirs(PDFPATH)

        options=get_param(BOOKID)
        print('options=',options)
        data['ebookId'] = BOOKID
        data['_nonce']=options.get('_nonce')
        data['_sign']=options.get('_sign')
        data['_timestamp']=options.get('_timestamp')
        print('data=',data)

        #print(data)
        res=requests.post(url,headers=headers,data=data)
        json_date = json.loads(res.text)
        #print(res.text)
        bookname=json_date.get('data').get('bookName')+'.pdf'
        datalist=json_date.get('data').get('data')
        for _data in datalist:
            #print(_data)
            imgurl=_data.get('imgurl')
            pagenum=_data.get('pageNo')
            print('开始下载第{}页...'.format(pagenum))
            get_page(pagenum,imgurl)
            print('下载第{}页完成'.format(pagenum))

        ##图片合并为一个pdf文件
        MergeImageToPdf(os.path.join(PDFPATH,bookname))
        time.sleep(2)