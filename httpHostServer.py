import ctypes
import sys

lib = ctypes.cdll.LoadLibrary('./HTTPSHost.cpython-310-x86_64-linux-gnu.so')
lib2 = ctypes.cdll.LoadLibrary('./test.cpython-310-x86_64-linux-gnu.so')

def start_server(ip='127.0.0.1',port=8000):
    lib.start_http_server(ip, port)

if __name__ == '__main__':
    ip = '127.0.0.1'
    port = 8000

    lib2.testFunc()
    sys.exit()

    if len(sys.argv) < 3:
        start_server()
    elif len(sys.argv) == 3:
        ip = sys.argv[1]
        port = int(sys.argv[2])

        start_server(ip=ip, port=port)


