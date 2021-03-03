import cv2 as cv
from flask import Flask, render_template, Response, redirect, request,flash
import datetime
import  time
import SMS



app = Flask(__name__)
cap = cv.VideoCapture(0)
cap.set(cv.CAP_PROP_FRAME_WIDTH,1280)
cap.set(cv.CAP_PROP_FRAME_HEIGHT,720)
cap.set(cv.CAP_PROP_FPS,25)

def generateFrames():
    timePassed = time.mktime(datetime.datetime.now().timetuple())
    # read the frames
    ret, frame1 = cap.read()
    ret, frame2 = cap.read()
    while cap.isOpened():
        # find the absolute difference between the first and second frame
        diff = cv.absdiff(frame1, frame2)
        # convert the difference to gray scale mode
        gray = cv.cvtColor(diff, cv.COLOR_BGR2GRAY)
        # blur the gray scale: kernel size is the second argument, Sigma x value is the third
        blur = cv.GaussianBlur(gray, (5, 5), 0)
        # find the threshold, we give the threshold interval, and the tyoe
        _, thresh = cv.threshold(blur, 30, 255, cv.THRESH_BINARY)
        # dilate the threshold image to fill in all the holes, to find better contours
        dilated = cv.dilate(thresh, None, iterations=3)
        # find the contour
        contours, _ = cv.findContours(dilated, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        # iterate through contours
        for contour in contours:
            # apply bounding rectangles for contours
            (x, y, w, h) = cv.boundingRect(contour)
            # if the area if smaller than the area of a person ignore, else we draw it
            if cv.contourArea(contour) < 5000:
                continue
            cv.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # print text on image if movement is observed
            cv.putText(frame1, "Status: {}".format('Movement detected'), (10, 20), cv.FONT_HERSHEY_SIMPLEX,
                      1, (0, 0, 255), 3)
        #add the current date to the streaming
        datet = str(datetime.datetime.now())
        cv.putText(frame1, datet, (10, 700), cv.FONT_HERSHEY_SIMPLEX, 1, (0,0, 0), 2, cv.LINE_AA)
        ret, buffer = cv.imencode('.jpg',frame1)
        frame1 = buffer.tobytes()

        currentTime = time.mktime(datetime.datetime.now().timetuple())
        if currentTime - timePassed < 3:
            SMS.sendMessage()
        #update streaming and upload it
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame1 + b'\r\n')
        frame1 = frame2
        # read the new frame
        ret, frame2 = cap.read()


@app.route('/video_feed')
def video_feed():
    return Response(generateFrames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')

if __name__=='__main__':
    app.run(host='ip')