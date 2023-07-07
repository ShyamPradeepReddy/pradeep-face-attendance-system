# pradeep-face-attendance-system
Face attendance system automatically scans your face so you don't need to touch anything to mark your attendance. A face recognition attendance system provides you with real-time data and syncs the data with no time lag. It helps organizations in efficient workforce management
import os
import pickle

import face_recognition
import cv2
import cvzone

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendencepradeep-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendencepradeep.appspot.com"
})
bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread("images/3352.png")
# imgBackground2 = cv2.imread("modes/1.png")

# imorting mode image in to list
folderModePath = 'modes'
modePathList = os.listdir(folderModePath)
imgModeList = []

for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

#load the encoding file
print("Loading encode file........")
file = open('encodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)

file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
# print(studentIds)

print("Encode file loaded.....")

modeType = 0
counter = 0
id = -1
imgStudent = []
while True:
    success, img = cap.read()



    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img

    imgBackground = imgBackground[:44 + 633, :808 + 414]
    imgBackground[44:44 + 504, 808:808 + 332] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("Matches", matches)
                        # print("facedis", faceDis)

            matchIndex = np.argmin(faceDis)


            if matches[matchIndex]:
                # print("Known face detected:")
                # print(studentIds[matchIndex])
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 * x1, 162 * y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                # cv2.imshow("Face Attendence", imgBackground)
                # cv2.waitKey(1)
                id = studentIds[matchIndex]
                # print(id)

                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading...", (275, 400))
                    cv2.imshow("Face Attendence", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1
        if counter != 0:
            if counter == 1:
                #data
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)
                #image

                blob = bucket.get_blob(f'image/{id}.jpg')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                #update data

                dataeTimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")

                secondsElapsed = (datetime.now()-dataeTimeObject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed>30:

                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 504, 808:808 + 332] = imgModeList[modeType]
                    cv2.waitKey(15)



            if modeType != 3:

                if 10<counter<20:
                     modeType = 2
                imgBackground[44:44 + 504, 808:808 + 332] = imgModeList[modeType]

                if counter<=10:
                    cv2.putText(imgBackground, str(studentInfo['total_attendance']), (843, 108), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (960, 400), cv2.FONT_HERSHEY_COMPLEX, 0.5, (50, 50, 50), 1)
                    cv2.putText(imgBackground, str(studentInfo['major']), (960, 450), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                        (50, 50, 50), 1)
                    cv2.putText(imgBackground, str(studentInfo['standard']), (880, 510), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['year']), (973, 510), cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (1053, 510), cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (332-w)//2


                    cv2.putText(imgBackground, str(studentInfo['name']), (798+offset, 360), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                    imgBackground[120:120 + 216, 870:870 + 216] = imgStudent
                    cv2.waitKey(5)

            counter+= 1

            if counter>=20:
                counter = 0
                modeType = 0
                studentInfo = []
                imgStudent = []
                imgBackground[44:44 + 504, 808:808 + 332] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0



    # cv2.imshow("webcam", img)
    cv2.imshow("Face Attendence", imgBackground)
    cv2.waitKey(1)
    # cv2.destroyAllWindows()
