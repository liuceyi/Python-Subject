#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
import requests
import cv2


class OCRAPI(object):
    AK = "45eff8f040b944f8bebe73e547835ac0"
    SK = "60d548276a02400f914d9ccf05e923f6"
    def GetAccessToken(self):
        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={}&client_secret={}'.format(AK, SK)
        response = requests.get(host)
        if response:
            res_json = response.json()
            access_token = res_json['access_token']
            return access_token
        return False
    # 通用文字识别（高精度版）
    def GetOCR(self):
        request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"
        # 二进制方式打开图片文件
        f = open('./test.jpg', 'rb')
        img = base64.b64encode(f.read())

        params = {"image":img}
        access_token = '[调用鉴权接口获取的token]'
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            print(response.json())





class UseCv:
    def __init__(self):
        self.path = 'lena.jpg'

    def cut(self):
        img = cv2.imread(self.path, flags=cv2.IMREAD_COLOR)
        bbox = cv2.selectROI(img, False)
        cut = img[bbox[1]:bbox[1]+bbox[3], bbox[0]:bbox[0]+bbox[2]]
        cv2.imwrite('cut.jpg', cut)




if __name__ == '__main__':
    UseCv().cut()





