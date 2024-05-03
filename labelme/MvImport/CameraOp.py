import sys
from PyQt5.QtWidgets import *
from .CamOperation_class import CameraOperation
from .MvCameraControl_class import *
from .MvErrorDefine_const import *
from .CameraParams_header import *
import ctypes


deviceList = MV_CC_DEVICE_INFO_LIST()
cam = MvCamera()
nSelCamIndex = 0
obj_cam_operation = 0
devideOpt = list()

# 获取选取设备信息的索引，通过[]之间的字符去解析
def TxtWrapBy(start_str, end, all):
    start = all.find(start_str)
    if start >= 0:
        start += len(start_str)
        end = all.find(end, start)
        if end >= 0:
            return all[start:end].strip()


# 将返回的错误码转换为十六进制显示
def ToHexStr(num):
    chaDic = {10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}
    hexStr = ""
    if num < 0:
        num = num + 2 ** 32
    while num >= 16:
        digit = num % 16
        hexStr = chaDic.get(digit, str(digit)) + hexStr
        num //= 16
    hexStr = chaDic.get(num, str(num)) + hexStr
    return hexStr


def enum_devices(mainWindow):
    global deviceList
    global obj_cam_operation

    deviceList = MV_CC_DEVICE_INFO_LIST()
    ret = MvCamera.MV_CC_EnumDevices(MV_GIGE_DEVICE | MV_USB_DEVICE, deviceList)
    if ret != 0:
        strError = "Enum devices fail! ret = :" + ToHexStr(ret)
        QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
    print("Find %d devices!" % deviceList.nDeviceNum)
    devlist = list()
    for i in range(0, deviceList.nDeviceNum):
        mvcc_dev_info = cast(deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
        strSerialNumber = ""
        for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
            if per == 0:
                break
            strSerialNumber = strSerialNumber + chr(per)
        print("user serial number: " + strSerialNumber)
        devlist.append(strSerialNumber)

    mainWindow._selectCameraComboBox.addItems(devlist)
    mainWindow._selectCameraComboBox.setCurrentIndex(0)



def open_device(mainWindow):
    global deviceList
    global nSelCamIndex
    global obj_cam_operation
    global devideOpt
    enum_devices(mainWindow)

    for index in range(0, deviceList.nDeviceNum):
        camera = MvCamera()
        opt = CameraOperation(camera, deviceList, index)
        devideOpt.append(opt)
        opt.Open_device()
        opt.Set_trigger_mode(False)
        opt.Get_parameter()
        opt.Start_grabbing()
    obj_cam_operation = devideOpt[0]
    return deviceList.nDeviceNum

def changeDevice(mainWindow, step = 1):
    global deviceList
    global nSelCamIndex
    global obj_cam_operation
    global cam
    global devideOpt
    stopGrab()
    n = deviceList.nDeviceNum
    nSelCamIndex = nSelCamIndex + step
    if(nSelCamIndex < 0):
        nSelCamIndex = nSelCamIndex + n
    nSelCamIndex = nSelCamIndex % n
    obj_cam_operation = devideOpt[nSelCamIndex]
    return nSelCamIndex

def changeDevice2(mainWindow, index = 1):
    global deviceList
    global nSelCamIndex
    global obj_cam_operation
    global cam
    global devideOpt
    stopGrab()
    nSelCamIndex = index
    obj_cam_operation = devideOpt[nSelCamIndex]
    return nSelCamIndex

def startGrab(mainWindow):
    obj_cam_operation.winHandle = mainWindow.canvas.winId()

def changeParam():
    obj_cam_operation.Set_parameter(2, 500000, 10)

def save_image(filename):
    global deviceList
    global devideOpt
    for index in range(0, deviceList.nDeviceNum):
        devideOpt[index].Save_jpg(filename)

def stopGrab():
    obj_cam_operation.winHandle = None

def closeGrab():
    global devideOpt
    print("Start stop thread")
    for obj in devideOpt:
        obj.Stop_grabbing()