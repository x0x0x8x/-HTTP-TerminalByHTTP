import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import cgi
import cv2
import string
import EncodeAES
import struct
import hashlib
import DataInImg
from urllib.parse import urlparse, parse_qs
import sshHost

#nohup ./exe &

homeUrl = 'http://127.0.0.1:8000'
current_work_path = os.path.abspath(sys.argv[0])
current_work_dir = os.path.dirname(current_work_path)

pagesPath = current_work_dir + '/pages'
imgPath = current_work_dir + '/img'
imgUrl = homeUrl + '/img'
indexHtml = pagesPath + '/index.html'
indexHtmlData = ''
pathL1 = 'L1/'
pathL2 = 'L2/'

key = 'jhzchfl'
head = b'~~~~~~~~~~~~~~~~~~~~~'

gl_oldCmdHashList = []
gl_oldCmdTimeList = []

__gl_ssh_server_thread = None
def encodeAES(data):
    global key
    return EncodeAES.encrypt(key, data)

def decodeAES(cipher):
    global key
    return EncodeAES.decrypt(key, cipher)

def scanCmdTimeList():
    for i in range(len(gl_oldCmdTimeList)):
        if time.time() - gl_oldCmdTimeList[0]> 5.0:
            #print(f'list pop >> [{gl_oldCmdHashList[0]}, {gl_oldCmdTimeList[0]}]')
            gl_oldCmdTimeList.pop(0)
            gl_oldCmdHashList.pop(0)
        else:
            break

def addHistoryList(hashValue, time):
    global gl_oldCmdHashList
    global gl_oldCmdTimeList
    gl_oldCmdHashList.append(hashValue)
    gl_oldCmdTimeList.append(time)

def findHashInList(data):
    global gl_oldCmdHashList
    hashValue = hashlib.sha256(data).hexdigest().encode()
    if hashValue in gl_oldCmdHashList:
        return True
    else:
        return False

def showCmdList():
    global gl_oldCmdHashList
    global gl_oldCmdTimeList
    for i in range(len(gl_oldCmdTimeList)):
        print(f'[{gl_oldCmdHashList[i]}]', end='')
        print(f'[{gl_oldCmdTimeList[i]}]', end='')
        print()

def loadHtml(url):
    if url == '/':
        with open(indexHtml, 'rb') as f:
            html = f.read()
    else:
        with open((pagesPath + url), 'rb') as f:
            html = f.read()
    return html, 'text/html'

def loadUrl(url):
    if url == '/':
        with open('index.html', 'rb') as f:
            data = f.read()
    else:
        if url[:1] == '/':
            url = url[1:]
        with open(url, 'rb') as f:
            data = f.read()
    return data,getUrlType(url)

def responseNormalCmd(selfClass, type, data):
    #print('response:',end='')
    #print(data)
    try:
        selfClass.send_response(200)
        selfClass.send_header('Content-type', type)
        selfClass.send_header('Connection', 'close')
        selfClass.end_headers()
        selfClass.wfile.write(data)
    except Exception as e:
        print(f'response normal error: {e}')

def responseClient(selfClass, isSeccess, type, data):
    try:
        if isSeccess:
            hashValue = hashlib.sha256(data).hexdigest().encode()
            data = encodeAES((b'ZBH ' + hashValue + data))
            selfClass.send_response(200)
            selfClass.send_header('Content-type', type)
            selfClass.send_header('Connection', 'close')
            selfClass.end_headers()
            selfClass.wfile.write(data)
        else:
            selfClass.send_response_only(404)
    except Exception as e:
        print(f'response client error: {e}')

def checkIsRealClient(clientSec, allClientData):
    if clientSec == 0:
        print('forgery attack !!!')
        return False
    curSec = time.time()
    if curSec - clientSec > 5 or findHashInList(allClientData):
        print('Replay attack !!!')
        return False
    else:
        return True

def getUrlType(url):
    #
    if url == '/' or url[-5:].lower() == '.html':
        return 'text/html'
    elif url[-4:].lower() == '.xml':
        return 'text/xml'
    elif url[-4:].lower() == '.txt':
        return 'text/plain'

    elif url[-4:].lower() == '.png':
        return 'image/png'
    elif url[-4:].lower() == '.jpg':
        return 'image/jpeg'
    elif url[-4:].lower() == '.gif':
        return 'image/gif'

    elif url[-4:].lower() == '.pdf':
        return 'application/pdf'
    elif url[-4:].lower() == '.json':
        return 'application/json'

    else:
        return 'application/octet-stream'

def dataToImg(data):
    #test
    imgUrl = 'img/Img8K.png'
    img = cv2.imread(imgUrl, cv2.IMREAD_UNCHANGED)
    DataInImg.setDataInImg(img, data, False)

    return img.tobytes()

def recvMultipart_form_data(selfClass,pdict):
    #print('is multipart/form-data')
    pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
    pdict['CONTENT-LENGTH'] = int(selfClass.headers['Content-Length'])
    #print('pdict : ', end='')
    #print(pdict)
    fields = cgi.parse_multipart(selfClass.rfile, pdict)
    return fields
def recvApplication_x_www_form_urlencoded(selfClass,pdict):
    content_length = int(selfClass.headers['Content-Length'])
    post_data = selfClass.rfile.read(content_length).decode('utf-8')
    parsed_data = parse_qs(post_data)

    # 提取特定字段
    name = parsed_data.get('name', [''])[0]
    age = parsed_data.get('age', [''])[0]

    return
def sshCommandHandle(selfClass, command = b''):
    global __gl_ssh_server_thread
    #print('***ssh command***')
    tag = command[:1]
    command = command[1:]
    if tag == b'0':
        print('ssh login')
        if __gl_ssh_server_thread:
            print('restarting...')
            sshHost.setHttpSshClient(False)
            __gl_ssh_server_thread.join()
            sshHost.setHttpSshClient(True)
        __gl_ssh_server_thread = threading.Thread(target=sshHost.start_server_by_other_queue)
        __gl_ssh_server_thread.start()
        responseClient(selfClass, True, 'text/plain', b'\1')
    elif tag == b'1':
        #ssh command
        print(b'push command>>> ' + command)
        if command == b'\x03' and not sshHost.getAppState():
            print('logout')
            sshHost.setHttpSshClient(False)
            __gl_ssh_server_thread.join()
            sshHost.setHttpSshClient(True)
            responseClient(selfClass, True, 'text/plain', b'\1')
        else:
            sshHost.push_ssh_command(command)
            responseClient(selfClass, True,'text/plain', b'\1')
    elif tag == b'2':
        # ssh get resp
        resp = sshHost.pop_ssh_response()
        if not resp:
            resp = b'\1'
        #print(b'pop resp>>> ' + resp)
        responseClient(selfClass, True, 'text/plain', resp)
    else:
        responseClient(selfClass, False, 'text/plain', b'invalid cmd')
    pass
def adminMsg(selfClass, allData):
    #print('admin msg')
    scanCmdTimeList()
    #showCmdList()

    clientSec = allData[:8]
    clientSec = struct.unpack('d', clientSec)[0]
    data = allData[8:]
    hashValue = data[:64]
    data = data[64:]
    #print(f'clientTime: {clientSec}')
    #print(f'hash: {hashValue}')
    #print(f'data: {data}')
    if hashlib.sha256(data).hexdigest().encode() != hashValue:
        print('hash not match')
        clientSec = 0

    if not checkIsRealClient(clientSec, data):
        print("not real client")
        urlRes, type = loadUrl(selfClass.path)
        responseNormalCmd(selfClass, type, urlRes)
    else:
        #print("real client")
        if data[:1] == b'1':
            #ssh command
            sshCommandHandle(selfClass, data[1:])
        else:
            responseClient(selfClass, True, 'application/png', b'recved >>>' + data)
        addHistoryList(hashlib.sha256(allData).hexdigest().encode(), clientSec)
def getHandle(selfClass):
    scanCmdTimeList()
    #showCmdList()
    print(f'get>>> {selfClass.path}')

    try:
        destUrl, contentType = loadUrl(selfClass.path)
        if contentType != '':
            if destUrl:
                selfClass.send_response(200)
                selfClass.send_header('Content-type', contentType)
                selfClass.send_header('Connection', 'close')
                selfClass.end_headers()
                selfClass.wfile.write(destUrl)

                return
        selfClass.send_response_only(404)
    except IOError as e:
        print(f'get I/O error: {e}')
    except Exception as e:
        print(f'error: {e}')
        selfClass.send_response_only(404)

def postHandle(selfClass):
    print(f'post >> {selfClass.path}')
    #print(selfClass.headers)
    global pathL1
    content_type, pdict = cgi.parse_header(selfClass.headers['Content-Type'])
    if content_type == 'multipart/form-data':
        data = recvMultipart_form_data(selfClass,pdict)
    elif content_type == 'application/x-www-form-urlencoded':
        data = recvApplication_x_www_form_urlencoded(selfClass,pdict)
    else:
        print('unkown content-type')
        selfClass.send_response_only(404)
    if 'PhotoGallery/UploadImg' in selfClass.path:
        data = data.get('file')[0]
        try:
            msg = EncodeAES.decrypt(key, data)
            #print(msg)
            if msg[:4] == b'ZBH ':
                adminMsg(selfClass, msg[4:])
            else:
                print('not admin')
                responseNormalCmd(selfClass, 'text/plain', b'image upload success')
        except Exception as e:
            print('not admin')
            responseNormalCmd(selfClass, 'text/plain', b'image upload success')
    else:
        selfClass.send_response_only(404)

    return

# 自定义请求处理类
class RequestHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        getHandle(self)
        #keep-alive???
        return
   
    def do_POST(self):
        postHandle(self)
        return
# 启动HTTP服务器
def run(server_class=HTTPServer, handler_class=RequestHandler, ip = '127.0.0.1', port=2052):

    server_address = ('127.0.0.1', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd on {ip}:{port}...')
    httpd.serve_forever()

def start_http_server(ip='127.0.0.1', port=8000):
    os.chdir('pages')
    run(ip=ip, port=port)

if __name__ == '__main__':
    ip = '127.0.0.1'
    port = 8000

    if len(sys.argv) < 3:
        run()
    elif len(sys.argv) == 3:
        ip = sys.argv[1]
        port = int(sys.argv[2])

        run(ip=ip, port=port)




