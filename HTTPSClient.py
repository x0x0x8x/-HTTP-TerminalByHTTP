import hashlib
import json
import random
import string
import struct

import requests
import EncodeAES
import time

key = 'jhzchfl'

def encodeAES(data):
    global key
    return EncodeAES.encrypt(key, data)

def decodeAES(cipher):
    global key
    return EncodeAES.decrypt(key, cipher)


def makeRandomCookie():
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
    timestamp = int(time.time())

    cookie = f'Hm_lvt_{random_string}={timestamp}'
    return  cookie

def makePostHeaders(host_ip='127.0.0.1', host_port=8000, url = ''):
    cookie = makeRandomCookie()
    headers = {
        'Host': f'{host_ip}:{host_port}',
        'Connection': 'keep-alive',
        'Content-Length': '0',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Upgrade-Insecure-Requests': '1',
        'Origin': f'http://{host_ip}:{host_port}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': url,
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cookie': cookie
    }
    return headers

def postMsgToHost(url,ip,port, data):
    headers = makePostHeaders(host_ip=ip,host_port=port,url=url)
    
    hashValue = hashlib.sha256(data).hexdigest().encode()
    
    curSec = time.time()
    #print(f'time: {curSec}')
    #print(f'hash: {hashValue}')
    #print(f'data: {data}')
    curSec = struct.pack('d', curSec)
    
    data = encodeAES((b'ZBH ' + curSec + hashValue + data))
    
    if data == None:
        print('encode fail')
        return None
    files = {
        'file': data
    }
    
    response = requests.post(url, files=files, headers=headers)

    requests.session().close()
    if response.status_code == 200:
        #print(b'>>>>')
        #print(response.content)
        data = decodeAES(response.content)
        if data == None:
            print('decode fail')
            return None
        if data[:4] != b'ZBH ':
            print('not real host resp')
            return None
        hashValue = data[4:64+4]
        data = data[64+4:]
        if hashlib.sha256(data).hexdigest().encode() == hashValue:
            return data
        else:
            print('forgery attack !!!')
            return None
    else:
        return None

def httpGetHtml(url):
    try:
        # 发送GET请求
        response = requests.get(url)
        # 检查响应状态码
        if response.status_code == 200:
            # 打印网页内容
            if response.headers['Content-type'] == 'text/html':
                response.encoding ='utf-8'
                return response.text
            else:
                return 'not html'
        else:
            print(f"Failed to get. Status code: {response.status_code}")
            return 'fail'
    except requests.RequestException as e:
        print(f"Error get: {e}")
        return 'fail'

def getDataFromImg(img):
    return img
def httpPost(url, data):
    global head
    try:
        data = postMsgToHost(url, data)
        if data:
            return data
        else:
            print(f"Failed to post data.")
            return None
    except requests.RequestException as e:
        print(f"Error post data: {e}")
        return None


if __name__ == "__main__":

    # 指定要请求的网页URL
    url = 'http://127.0.0.1:8000/page1.html'
    baidu = 'https://fanyi.baidu.com/mtpe-individual/multimodal?aldtype=16047&ext_channel=Aldtype#/en/zh/'
    #fetch_webpage(url)
