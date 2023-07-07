import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://faceattendencepradeep-default-rtdb.firebaseio.com/'
})

ref = db.reference('Students')
data = {
    "3351":
        {
            "name": "Pradeep Reddy",
            "major": "Computer Science",
            "starting_year": 2022,
            "total_attendance": 99,
            "year": 1,
            "standard": "a",
            "last_attendance_time": "2023-07-06 18:09:00"

        },
    "3352":
        {
            "name": "Elon musk",
            "major": "Aiml",
            "starting_year": 2021,
            "total_attendance": 0,
            "year": 1,
            "standard": "d",
            "last_attendance_time": "2023-07-06 18:09:00"

        },
    "3353":
        {
            "name": "Jeff Bezoz",
            "major": "Aids",
            "starting_year": 2020,
            "total_attendance": 0,
            "year": 1,
            "standard": "d",
            "last_attendance_time": "2023-07-06 18:09:00"

        },
    "3354":
        {
            "name": "Ryan Renolds",
            "major": "cic",
            "starting_year": 2019,
            "total_attendance": 80,
            "standard": "d",
            "year": 1,
            "last_attendance_time": "2023-07-06 18:09:00"

        }
}

for key,value in data.items():
    ref.child(key).set(value)
