import numpy as np
import pydicom as dicom
import time
import datetime
import skimage
from skimage import transform

WIDTH_SCALE = 4  # 将人体PET图像按比例放大多少倍 默认放大四倍


def _read_dicom_series(directory, filepattern="PT_*"):
    '''
    读取dicom格式的图像
    :param directory: PET图像序列存储文件夹
    :param filepattern: 每个图像满足的格式
    :return: pixel_array像素值信息 生物学信息，像素值放缩比
    '''
    import os
    import natsort
    import glob
    if not os.path.exists(directory) or not os.path.isdir(directory):
        raise ValueError("Given directory does not exist or is a file : " + str(directory))
    # print('\tRead Dicom', directory)
    lstFilesDCM = natsort.natsorted(glob.glob(os.path.join(directory, filepattern)))
    # print('\tLength dicom series', len(lstFilesDCM))
    # Get ref file
    RefDs = dicom.read_file(lstFilesDCM[0])
    # Load dimensions based on the number of rows, columns, and slices (along the Z axis)
    ConstPixelDims = (int(RefDs.Rows), int(RefDs.Columns), len(lstFilesDCM))
    # The array is sized based on 'ConstPixelDims'
    ArrayDicom = np.zeros(ConstPixelDims, dtype=RefDs.pixel_array.dtype)
    slopes = np.zeros(ConstPixelDims[2])
    # loop through all the DICOM files
    for filenameDCM in lstFilesDCM:
        # read the file
        ds = dicom.read_file(filenameDCM)
        # store the raw image data
        ArrayDicom[:, :, lstFilesDCM.index(filenameDCM)] = ds.pixel_array
        slopes[lstFilesDCM.index(filenameDCM)] = ds.get('RescaleSlope')
    return ArrayDicom, RefDs, slopes


def getASuv(filePath=r'E:\pyWorkspace\testDataset\PT00998-2\5\PT_128'):
    meta = dicom.read_file(filePath)
    pixel = meta.pixel_array
    slope = meta.get('RescaleSlope')
    weightKg = meta.get('PatientWeight')
    # 患者身高
    heightCm = meta.get('PatientSize') * 100  # 身高以厘米为单位
    # 患者性别
    sex = meta.get("PatientSex")
    # 示踪剂注射总剂量
    tracerActivity = meta.get('RadiopharmaceuticalInformationSequence')[0].get('RadionuclideTotalDose')
    theDate = meta.get('SeriesDate')
    measureTime = meta.get('RadiopharmaceuticalInformationSequence')[0].get('RadiopharmaceuticalStartTime')
    measureTime = time.strptime(theDate + measureTime[0:6], '%Y%m%d%H%M%S')
    measureTime = datetime.datetime(*measureTime[:6])
    # scanTime=meta.get('SeriesDate')+meta.get('SeriesTime')
    scanTime = meta.get('SeriesTime')
    scanTime = time.strptime(theDate + scanTime, '%Y%m%d%H%M%S')
    scanTime = datetime.datetime(*scanTime[:6])
    halfTime = meta.get('RadiopharmaceuticalInformationSequence')[0].get('RadionuclideHalfLife')
    if (scanTime > measureTime):
        actualActivity = tracerActivity * (2) ** (-(scanTime - measureTime).seconds / halfTime)
    else:
        raise ('time wrong:scanTime should be later than measure')

    if sex == 'F':
        lbmKg = 1.07 * weightKg - 148 * (weightKg / heightCm) ** 2
    else:
        lbmKg = 1.10 * weightKg - 120 * (weightKg / heightCm) ** 2

    suvLbm = pixel * slope * lbmKg * 1000 / actualActivity
    # suv=np.uint8(suvLbm)
    return suvLbm


def _calSuv(pixels, meta, slopes):
    '''
    计算SUV值
    :param pixels: 图像的像素点值矩阵
    :param meta: 图像的相关生物学信息
    :param slopes: 像素值放缩比
    :return: numpy三维数组，表示SUV值
    '''
    # 患者体重
    weightKg = meta.get('PatientWeight')
    # 患者身高
    heightCm = meta.get('PatientSize') * 100  # 身高以厘米为单位
    # 患者性别
    sex = meta.get("PatientSex")
    # 示踪剂注射总剂量
    tracerActivity = meta.get('RadiopharmaceuticalInformationSequence')[0].get('RadionuclideTotalDose')
    theDate = meta.get('SeriesDate')
    measureTime = meta.get('RadiopharmaceuticalInformationSequence')[0].get('RadiopharmaceuticalStartTime')
    measureTime = time.strptime(theDate + measureTime[0:6], '%Y%m%d%H%M%S')
    measureTime = datetime.datetime(*measureTime[:6])
    # scanTime=meta.get('SeriesDate')+meta.get('SeriesTime')
    scanTime = meta.get('SeriesTime')
    scanTime = time.strptime(theDate + scanTime, '%Y%m%d%H%M%S')
    scanTime = datetime.datetime(*scanTime[:6])
    halfTime = meta.get('RadiopharmaceuticalInformationSequence')[0].get('RadionuclideHalfLife')
    if (scanTime > measureTime):
        actualActivity = tracerActivity * (2) ** (-(scanTime - measureTime).seconds / halfTime)
    else:
        raise ('time wrong:scanTime should be later than measure')

    if sex == 'F':
        lbmKg = 1.07 * weightKg - 148 * (weightKg / heightCm) ** 2
    else:
        lbmKg = 1.10 * weightKg - 120 * (weightKg / heightCm) ** 2

    suvLbm = np.zeros(pixels.shape)
    for i in range(pixels.shape[2]):
        suvLbm[:, :, i] = pixels[:, :, i] * slopes[i] * lbmKg * 1000 / actualActivity

    return suvLbm


def getSUV(path):
    '''
    计算给定路径下所有PET图像的SUV值，并进行不同维度上的单位化
    :param path: PET图像序列的路径
    :return: numpy三维数组，表示一个人体各处的SUV值
    '''
    pixels, meta, slopes = _read_dicom_series(path)
    suvLbm = _calSuv(pixels, meta, slopes)

    pixelSpacing = meta.get('PixelSpacing')
    sliceThickness = float(meta.get('SliceThickness'))
    suvFullOnSlice = np.zeros(np.multiply(suvLbm.shape, [WIDTH_SCALE, WIDTH_SCALE, 1]))

    for i in range(suvFullOnSlice.shape[2]):  # 逐层插值
        suvFullOnSlice[:, :, i] = skimage.transform.rescale(suvLbm[:, :, i], [WIDTH_SCALE, WIDTH_SCALE])

    sliceScale = WIDTH_SCALE * sliceThickness / pixelSpacing[0]
    suvFull = np.zeros(np.int16(np.multiply(suvFullOnSlice.shape, [1, 1, sliceScale])))
    for i in range(suvFull.shape[1]):  # 层间插值
        suvFull[i, :, :] = skimage.transform.resize((suvFullOnSlice[i, :, :]), [suvFull.shape[0], suvFull.shape[2]])
    suvFull = np.transpose(suvFull, (0, 2, 1))
    return suvFull


def getCT(path):
    pixels, meta, slopes = _read_dicom_series(path)
    suvLbm = _calSuv(pixels, meta, slopes)

    pixelSpacing = meta.get('PixelSpacing')
    sliceThickness = float(meta.get('SliceThickness'))
    suvFullOnSlice = np.zeros(np.multiply(suvLbm.shape, [WIDTH_SCALE, WIDTH_SCALE, 1]))

    for i in range(suvFullOnSlice.shape[2]):  # 逐层插值
        suvFullOnSlice[:, :, i] = skimage.transform.rescale(suvLbm[:, :, i], [WIDTH_SCALE, WIDTH_SCALE])

    sliceScale = WIDTH_SCALE * sliceThickness / pixelSpacing[0]
    suvFull = np.zeros(np.int16(np.multiply(suvFullOnSlice.shape, [1, 1, sliceScale])))
    for i in range(suvFull.shape[1]):  # 层间插值
        suvFull[i, :, :] = skimage.transform.resize((suvFullOnSlice[i, :, :]), [suvFull.shape[0], suvFull.shape[2]])
    suvFull = np.transpose(suvFull, (0, 2, 1))
    return suvFull


def testSUV():
    rootP = 'F:\数据集\淋巴瘤原始更多\淋巴瘤图像'  # 将这里改成所有文件的根目录
    patients = ['PT00998-2', 'PT01282-4', 'PT02522-3', 'PT05738-2', 'PT06044-2',
                'PT38947', 'PT39061', 'PT39188', 'PT39342', 'PT39387', 'PT39520',
                'PT39620', 'PT39741', 'PT39748', 'PT39758', 'PT39849', 'PT39851',
                'PT39858', 'PT39872', 'PT39874', 'PT39929']  # 将这里改成所有病人的ID
    for i in range(len(patients)):
        tPath = os.path.join(rootP, patients[i], str(5))
        imgs = getSUV(path=tPath)
        with open(os.path.join(tPath, 'suvpkl'), 'wb') as f:
            pickle.dump(imgs, f)


if __name__ == '__main__':
    import pickle
    import os
    import natsort
    import glob

    rootP = 'F:\数据集\淋巴瘤原始更多\淋巴瘤图像'  # 将这里改成所有文件的根目录
    patients = ['PT00998-2', 'PT01282-4', 'PT02522-3', 'PT05738-2', 'PT06044-2',
                'PT38947', 'PT39061', 'PT39188', 'PT39342', 'PT39387', 'PT39520',
                'PT39620', 'PT39741', 'PT39748', 'PT39758', 'PT39849', 'PT39851',
                'PT39858', 'PT39872', 'PT39874', 'PT39929']  # 将这里改成所有病人的ID
    for i in range(len(patients)):
        tPath = os.path.join(rootP, patients[i], str(4))
        imgs = getCT(path=tPath)
