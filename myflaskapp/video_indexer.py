import cv2     # for capturing videos
import os
# import pytesseract
# from torch import prelu
# pytesseract.pytesseract.tesseract_cmd="C:/Program Files/Tesseract-OCR/tesseract.exe"
import math   # for mathematical operations
# import matplotlib.pyplot as plt    # for plotting the images
# import pandas as pd
# from keras.preprocessing import image   # for preprocessing the images
# import numpy as np    # for mathematical operations
# from keras.utils import np_utils
# from skimage.transform import resize   # for resizing images
from skimage.metrics import structural_similarity as ssim
from google.cloud import vision

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'static/auth/ServiceAccountToken.json'
client = vision.ImageAnnotatorClient()

video_file = "cloud-computing.mp4"

def frame_fetcher(videoFile):
    # videoFile = "aiml.mp4"

    count = 0
    cap = cv2.VideoCapture(videoFile)   # capturing the video from the given path
    frameRate = cap.get(5) #frame rate
    no_of_frames = cap.get(7)

    old_image = None
    im_set={}

    while(cap.isOpened()):
        frameId = cap.get(1) #current frame number
        if frameId%1000==0:
            print('{:.0f} / {:.0f} frames parsed'.format(frameId,no_of_frames), end='\r')
        ret, frame = cap.read()
        if (ret != True):
            break
        if (frameId % (5 * math.floor(frameRate)) == 0):

            image = frame
            if image is not None:
                if old_image is None:
                    old_image = image

                if ssim(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY),cv2.cvtColor(old_image, cv2.COLOR_BGR2GRAY))<=0.80:
                    old_image = image
                    im_set[count] = image
            count+=1

    # print(frameId)
    # print(im_set.keys())    
    print('\n')
    cap.release()

    return im_set
    
def chapter_fetcher(videoFile, frames_list):
    # videoFile = "aiml.mp4"

    count = 0
    cap = cv2.VideoCapture(videoFile)   # capturing the video from the given path
    frameRate = cap.get(5) #frame rate
    no_of_frames = cap.get(7)

    im_set={}

    while(cap.isOpened()):
        frameId = cap.get(1) #current frame number
        if frameId%1000==0:
            print('{:.0f} / {:.0f} frames parsed'.format(frameId,no_of_frames), end='\r')
        ret, frame = cap.read()
        if (ret != True):
            break
        if (frameId % (5 * math.floor(frameRate)) == 0):

            image = frame
            if image is not None and len(frames_list)!=0:
                
                gcp_image = vision.Image(content=cv2.imencode('.jpg', image)[1].tobytes())
                response = client.document_text_detection(image=gcp_image)
                text = response.full_text_annotation.text

                # text = pytesseract.image_to_string(image)
                chapter_text = frames_list[0]

                # text = text.replace('\n',' ')
                # text = text.replace('"',' ')
                # text = text.replace("'",' ')
                # text = text.replace('/7/',' ')
                # text = text.replace('|',' ')
                # text = text.replace('!',' ')

                # flag = True

                # for word in chapter_text:
                #     if word not in text:
                #         flag = False

                if chapter_text in text:
                    im_set[count] = image
                    frames_list.pop(0)
            else:
                print('/r/n')
                break
            count+=1

    # print(frameId)
    # print(im_set.keys())    
    print('\n')
    cap.release()

    return im_set, frameRate, no_of_frames

def index_video(video_file):

    key_images_set = frame_fetcher(video_file)

    # print(key_images_set.keys())

    key_text_set = {}

    for key in key_images_set.keys():
        image = vision.Image(content=cv2.imencode('.jpg', key_images_set[key])[1].tobytes())
        response = client.document_text_detection(image=image)

        key_text_set[key] = response.full_text_annotation.text


    # print(key_text_set.values())

    for key in list(key_text_set.keys()):

        terms = key_text_set[key].split('\n')

        if '' in terms:
            terms.remove('')

        if len(terms)>=2:
            key_text_set[key] = terms
        else:
            del key_text_set[key]

    del key_text_set[list(key_text_set.keys())[-1]]

    key_terms = []
    key_terms_set = {}
    chars = ['=','+','.','-','/','(',')','©',':','三'] + [str(x) for x in range(10)]

    for key in list(key_text_set.keys()):

        terms = []
        for term in key_text_set[key]:
            if term not in key_terms and len(term)>1 and term == term.title() and all([x not in term for x in chars]):
                terms.append(term)
                key_terms.append(term)

        key_terms_set[key] = terms

    frames_list = key_terms.copy()

    print(frames_list)

    chapters_set, frame_rate, no_of_frames = chapter_fetcher(video_file,frames_list)

    # chap_names = ['START','Explain AI/ML/DL/DS','Machine Learning','Deep Learning & Neural Networks','END']

    chap_names = ['START'] + key_terms + ['END']

    # print(len(chapters_set.keys()))
    # print(len(chap_names))
    chapters = [ {'title': chap_names[i], 'startTime' : '{:02.0f}:{:02.0f}:{:02.0f}.010'.format(key *5//3600,key * 5//60,key * 5%60)} for i,key in enumerate([0.2] + list(chapters_set.keys())+ [no_of_frames//(5*frame_rate)])]

    distinct_times = []

    text =""

    for i in range(len(chapters)-1):
        chap = chapters[i]
        title = chap['title']
        start = chap['startTime']

        if start not in distinct_times:
            distinct_times.append(start)

        end = chapters[i+1]['startTime'][:-3] + '000'

        text += f"""{title};{start};{end}\n"""

    with open("{}txt".format(video_file[:-3]),"w") as myfile:
        myfile.write(text)