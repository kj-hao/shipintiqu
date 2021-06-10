# base64是一种将不可见字符转换为可见字符的编码方式
import base64
# opencv是跨平台计算机视觉库，实现了图像处理和计算机视觉方面的很多通用算法
import os

import cv2
import requests
#from aip import AipOcr
# 百度AI的文字识别库

#%%剪切视频，以图片形式输出
def tailor_video(video_path):
    times = 0
    # 提取视频的频率，每10帧提取一个
    frameFrequency = 10
    # 输出图片到当前目录video文件夹下
    outPutDirName = video_path[:-4] + '/'
    if not os.path.exists(outPutDirName):
        # 如果文件目录不存在则创建目录
        os.makedirs(outPutDirName)
    camera = cv2.VideoCapture(video_path)
    
    
    # 帧频
    fps = camera.get(cv2.CAP_PROP_FPS)
    # 视频总帧数
    total_frames = int(camera.get(cv2.CAP_PROP_FRAME_COUNT))
    # 图像尺寸
    image_size = (int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)))
    print('帧频',fps)
    print('视频总帧数',total_frames)
    print('图像尺寸',image_size)
    
    while True:
        times += 1
        res, image = camera.read()
        if not res:
            print('not res , not image')
            break
        if times % frameFrequency == 0:
            cv2.imwrite(outPutDirName + str(times) + '.jpg', image)  #文件目录下将输出的图片名字命名为10.jpg这种形式

#%%创建文本，存放文字信息
def text_create(name, msg):
    full_path = name + '.txt'  # 也可以创建一个.doc的word文档
    file = open(full_path, 'w')
    file.write(msg)
    file.close()
    
#%%定义一个函数，用来判断是否是中文，是中文的话就返回True代表要提取中文字幕
def is_Chinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

#%%剪辑字幕
def tailor(path1,path2,begin,end,step_size):  #截取字幕
    for i in range(begin,end,step_size):
        fname1=path1 % str(i)
        img = cv2.imread(fname1)
        cropped = img[320:350, :]  # 裁剪坐标为[y0:y1, x0:x1]
        imgray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        thresh = 200
        ret, binary = cv2.threshold(imgray, thresh, 255, cv2.THRESH_BINARY)  # 输入灰度图，输出二值图
        binary1 = cv2.bitwise_not(binary)  # 取反
        cv2.imwrite(path2 % str(i), binary1)
#%%# 定义一个函数，用来访问百度API，
def requestApi(img):
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
    params = {"image": img,'language_type':'CHN_ENG'}
    access_token = '24.6eef8834c6d4ac941d32755f2edb0739.2592000.1620818774.282335-23977204'#需要根据不同的电脑更换
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    results=response.json()
    return results

#%%读取图片和字幕
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        # 将读取出来的图片转换为b64encode编码格式
        return base64.b64encode(fp.read())
# 定义函数字幕，用来对字幕进行操作
# step_size 步长
def subtitle(path2,begin,end,step_size):
    array =[] #定义一个数组用来存放words
    for i in range(begin,end,step_size):  #begin开始，end结束，循环按照步长step_size遍历，共有419张图片，也就是（1,420,10）
        fname1=path2 % str(i)
        image = get_file_content(fname1)
        try:
            results=requestApi(image)['words_result']  #调用requestApi函数，获取json字符串中的words_result
            for item in results:
                array.append(item['words'])
        except Exception as e:
            print(e)

    text=''
    result = list(set(array))  # 将array数组准换为一个无序不重复元素集达到去重的效果，再转为列表
    result.sort(key=array.index) # 利用sort将数组中的元素即字幕重新排序，达到视频播放字幕的顺序
    for item in result:
        text += item+'\n'
    text_create('output_subtitle',text)

#%%主方法控制台运行输出
if __name__ =="__main__":
    video_path = '238664234-1-16.mp4'
    path1 = video_path[:-4] + '/%s.jpg'  # 视频转为图片存放的路径（帧）
    cut = 'cut'
    path2 = cut+'/%s.jpg'  # 图片截取字幕后存放的路径
    if not os.path.exists(cut):
         # 如果文件目录不存在则创建目录
         os.makedirs(cut)
    print("""
          1.原始视频-->按帧显示图片
          2.按帧显示图片-->剪切后灰度处理的字幕图片
          3.剪切后灰度处理的字幕图片-->字幕文档
          4.原始图片-->字母提取文档
          """)
    choose=input('输入你要实现的功能：')
    begin=10
    end=19963
    step_size=10
    if choose=='1':
        tailor_video(video_path)
    if choose=='2':
        tailor(path1,path2,begin,end,step_size)
    if choose=='3':
        subtitle(path2,begin,end,step_size)
    if choose=='4':
        print('原始视频-->按帧显示图片')
        tailor_video(video_path)
        print('按帧显示图片-->剪切后灰度处理的字幕图片')
        tailor(path1,path2,begin,end,step_size)
        print('剪切后灰度处理的字幕图片-->字幕文档')
        subtitle(path2,begin,end,step_size)
