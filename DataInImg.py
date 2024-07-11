import cv2
import bitarray
import numpy as np
import EncodeAES
#pip3 install opencv-python
#pip3 install bitarray
#pip3 install cryptography

# 定义一个函数来打印每个像素的值
def print_pixels(image_array):
    height, width, channels = image_array.shape
    for i in range(height):
        for j in range(width):
            pixel_value = image_array[i, j, :]
            print(f"Pixel at ({i}, {j}): {pixel_value}")
def initImg(image_array):
    height, width, ch = image_array.shape
    for i in range(height):
        for j in range(width):
            pixel_value = image_array[i, j, :]
            pixel_value[0] = pixel_value[0] >> 1 << 1
            pixel_value[1] = pixel_value[1] >> 1 << 1
            pixel_value[2] = pixel_value[2] >> 1 << 1
def setDataInImg(image_array, data, cut):
    height, width, ch  = image_array.shape
    bitLen = len(data) * 8
    if bitLen + 64 >height*width*3:
        print('data too long')
        return None

    index = 0
    metaIndex = 0
    lenBitArr = bitarray.bitarray()
    dataBitArr = bitarray.bitarray()

    lenBitArr.frombytes(bitLen.to_bytes(8,'big'))
    dataBitArr.frombytes(data)
    tmp = bitarray.bitarray()
    for i in range(height):
        for j in range(width):
            if index >= bitLen:
                if cut:
                    image_array = image_array[:i+1,:]
                return image_array
            pixel_value = image_array[i, j, :]
            if metaIndex < 64:
                if lenBitArr[metaIndex]:
                    pixel_value[0] |= (np.uint8(1))
                else:
                    pixel_value[0] &= ~(np.uint8(1))
                metaIndex += 1
            elif index < bitLen:
                if dataBitArr[index]:
                    pixel_value[0] |= (np.uint8(1))
                    tmp.append(1)
                else:
                    pixel_value[0] &= ~(np.uint8(1))
                    tmp.append(0)
                index += 1

            if metaIndex < 64:
                if lenBitArr[metaIndex]:
                    pixel_value[1] |= (np.uint8(1))
                else:
                    pixel_value[1] &= ~(np.uint8(1))
                metaIndex += 1
            elif index < bitLen:
                if dataBitArr[index]:
                    pixel_value[1] |= (np.uint8(1))
                    tmp.append(1)
                else:
                    pixel_value[1] &= ~(np.uint8(1))
                    tmp.append(0)
                index += 1
            if metaIndex < 64:
                if lenBitArr[metaIndex]:
                    pixel_value[2] |= (np.uint8(1))
                else:
                    pixel_value[2] &= ~(np.uint8(1))
                metaIndex += 1
            elif index < bitLen:
                if dataBitArr[index]:
                    pixel_value[2] |= (np.uint8(1))
                    tmp.append(1)
                else:
                    pixel_value[2] &= ~(np.uint8(1))
                    tmp.append(0)
                index += 1
def setDataInImg2(image_array, data, cut):
    height, width, ch  = image_array.shape
    bitLen = len(data) * 8
    if bitLen + 8 >height*width*3:
        print('data too long')
        return None

    index = 0
    metaIndex = 0
    lenBitArr = bitarray.bitarray()
    dataBitArr = bitarray.bitarray()

    lenBitArr.frombytes(bitLen.to_bytes(8))
    dataBitArr.frombytes(data)
    tmp = bitarray.bitarray()
    for i in range(height):
        for j in range(width):
            if index >= bitLen:
                if cut:
                    image_array = image_array[:i+1,:j+1]
                return image_array
            pixel_value = image_array[i, j, :]
            if metaIndex < 64:
                if lenBitArr[metaIndex]:
                    pixel_value[0] |= (np.uint8(1))
                else:
                    pixel_value[0] &= ~(np.uint8(1))
                metaIndex += 1
            elif index < bitLen:
                if dataBitArr[index]:
                    pixel_value[0] |= (np.uint8(1))
                    tmp.append(1)
                else:
                    pixel_value[0] &= ~(np.uint8(1))
                    tmp.append(0)
                index += 1

            if metaIndex < 64:
                if lenBitArr[metaIndex]:
                    pixel_value[1] |= (np.uint8(1))
                else:
                    pixel_value[1] &= ~(np.uint8(1))
                metaIndex += 1
            elif index < bitLen:
                if dataBitArr[index]:
                    pixel_value[1] |= (np.uint8(1))
                    tmp.append(1)
                else:
                    pixel_value[1] &= ~(np.uint8(1))
                    tmp.append(0)
                index += 1
            if metaIndex < 64:
                if lenBitArr[metaIndex]:
                    pixel_value[2] |= (np.uint8(1))
                else:
                    pixel_value[2] &= ~(np.uint8(1))
                metaIndex += 1
            elif index < bitLen:
                if dataBitArr[index]:
                    pixel_value[2] |= (np.uint8(1))
                    tmp.append(1)
                else:
                    pixel_value[2] &= ~(np.uint8(1))
                    tmp.append(0)
                index += 1
def getDataFromImg(image_array):
    height, width, ch  = image_array.shape
    bitLen = 0

    index = 0
    metaIndex = 0
    data = b''
    lenBitArr = bitarray.bitarray(64)
    dataBitArr = bitarray.bitarray()
    for i in range(height):
        for j in range(width):
            if index >= bitLen and bitLen > 0:
                data = dataBitArr.tobytes()
                return data
            pixel_value = image_array[i, j, :]
            if metaIndex < 64:
                if pixel_value[0] & (np.uint8(1)):
                    lenBitArr[metaIndex] = 1
                else:
                    lenBitArr[metaIndex] = 0
                metaIndex += 1
                if metaIndex == 64:
                    bitLen = int.from_bytes(lenBitArr.tobytes())
                    dataBitArr = bitarray.bitarray(bitLen)
            elif index < bitLen:
                if  pixel_value[0] & (np.uint8(1)):
                    dataBitArr[index] = 1
                else:
                    dataBitArr[index] = 0
                index += 1

            if metaIndex < 64:
                if pixel_value[1] & (np.uint8(1)):
                    lenBitArr[metaIndex] = 1
                else:
                    lenBitArr[metaIndex] = 0
                metaIndex += 1
                if metaIndex == 8:
                    bitLen = int.from_bytes(lenBitArr.tobytes())
                    dataBitArr = bitarray.bitarray(bitLen)
            elif index < bitLen:
                if  pixel_value[1] & (np.uint8(1)):
                    dataBitArr[index] = 1
                else:
                    dataBitArr[index] = 0
                index += 1

            if metaIndex < 64:
                if pixel_value[2] & (np.uint8(1)):
                    lenBitArr[metaIndex] = 1
                else:
                    lenBitArr[metaIndex] = 0
                metaIndex += 1
                if metaIndex == 8:
                    bitLen = int.from_bytes(lenBitArr.tobytes())
                    dataBitArr = bitarray.bitarray(bitLen)
            elif index < bitLen:
                if  pixel_value[2] & (np.uint8(1)):
                    dataBitArr[index] = 1
                else:
                    dataBitArr[index] = 0
                index += 1
    data = dataBitArr.tobytes()
    return data

def test(image_path = 'src.png', outPath = 'dest.png'):
    # 打开图像文件
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # 以不改变的方式读取图像
    # 打印图像形状（高度、宽度、通道数）
    height, width, ch = img.shape
    print(f"可容纳最大数据: {(height*width*3 - 8*8)/8}byte")
    print("图像形状:", img.shape)
    print("位深度:", img.dtype)
    # 打印部分像素值
    #print_pixels(img[:, :, :])  # 打印前5行前5列的像素值

    initImg(img)

    data = '''
    隐写术是信息隐藏技术在隐蔽通信方面的一个重要应用。它是将秘密信息隐藏于一个公开的载体媒
介当中，通过公开载体媒介的传输，实现秘密信息的安全传输。JPEG图像压缩格式可以实现很高的压缩
率，同时能够保证良好的图像质量，在互联网和日常生活中被广泛使用。因此以 JPEG 图像作为载体的
信息隐藏算法研究具有重要的理论和实际应用价值。 
以JPEG图像为载体的典型隐写方法有Jsteg [1] [2]、Outguess [3]、F5 [4]等。其中Jsteg嵌入方法会
引起系数直方图出现值对趋于相等的异常[5]，容易被基于直方图统计特性的隐写算法所检测，如卡方分
析，安全性较差。Outguess方法在Jsteg方法的基础上通过牺牲一半的信息隐藏容量来修正由于信息嵌入
引起的直方图改变，虽然能够较好地保持JPEG图像DCT系数直方图统计特性，但是信息隐藏容量有限。
F5 方法能够较好地保持JPEG图像DCT系数直方图特性，同时能够取得较大的信息隐藏容量，但是信息
嵌入时DCT系数直方图中会出现0值两边的数值向中间收缩，值为0的DCT系数的个数明显增加的情
况，即“收缩”(Shrinkage)现象，这一点容易被攻击者所利用[6]。 
JPEG 图像一阶直方图统计特性[4]，作为 JPEG图像的基本特征，经常被用于JPEG图像的隐写检测。
如何提出新的嵌入策略实现在不牺牲信息隐藏容量的情况下，较好保持 JPEG 图像直方图统计特性，具
有重要意义。 
文献[7] [8]中指出提高嵌入效率，最大限度地减少由于信息嵌入对载体造成的影响是增强隐写方法安
全性的一个重要途径。隐写编码可以有效提高信息嵌入效率，减少信息嵌入对原始载体的改动及影响。
矩阵编码[4]是最早被用于提高嵌入效率的编码方法。当矩阵编码参数为(
 1, 2
 k
 −
 1,
 k
 )
 k −
个载体数据中嵌入k比特秘密信息，而最多仅需改动其中的1个载体数据。Filler 等人在文献[9]中提出
STC (syndrome-trellis codes)编码方法，与矩阵编码方法相比，可以实现更高的嵌入效率。 
时，可以实现在2 1
基于上述分析，本文结合STC编码方法，并通过控制低频部分用于信息嵌入的绝对值为1的DCT
系数比例来保持DCT系数直方图统计特性，提出了一种新的以JPEG图像为载体的隐写方法。实验结果
表明，该方法与Jsteg 方法、F5 方法相比，不仅可以实现更大的信息隐藏容量和更高的嵌入效率，而且
隐秘图像具有更好的图像质量，同时可以较好地保持JPEG图像DCT系数直方图统计特性，能够抵抗一
般的基于直方图统计特性的隐写检测。
    '''

    with open('A Relational Model of Data for Large Shared Data Banks.pdf', 'rb') as f:
        data = f.read()
    key = 'jhzchfl'
    data = EncodeAES.encrypt(key, data)
    print(f'待写入数据{len(data)}byte')
    img = setDataInImg(img, data, True)
    if img.all() == None:
        return
    print("图像形状:", img.shape)
    cv2.imwrite(outPath, img)#, [cv2.IMWRITE_PNG_COMPRESSION,9]

    img = cv2.imread(outPath, cv2.IMREAD_UNCHANGED)
    print("位深度:", img.dtype)
    data = getDataFromImg(img)
    if data == None:
        print('none data?')
        return
    data = EncodeAES.decrypt(key, data)
    with open('out.pdf', 'wb') as f:
        f.write(data)
    #print(data.decode())

#test('152777-chou_xiang_yi_shu-yi_shu_zuo_pin-fen_xing_ji_shu-se_cai-lu_se_de-7680x4320.png','152777-chou_xiang_yi_shu-yi_shu_zuo_pin-fen_xing_ji_shu-se_cai-lu_se_de-7680x4320_out.png')

'''
img = cv2.imread('F:\\MoveDisk\\1\\out.png', cv2.IMREAD_UNCHANGED)
print("位深度:", img.dtype)
data = getDataFromImg(img)
if data == None:
    print('none data?')
    exit(0)
data = EncodeAES.decrypt('jhzchfl', data)
print(data)
'''
