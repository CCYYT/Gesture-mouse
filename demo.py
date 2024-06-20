import math
import time
import cv2  
import mediapipe as mp  
import numpy as np
  

click_down_flag = 0
click_up_flag = 0
click_down_time = 0
# up_fingers凸包外的点, list_lms所有点的坐标
def gesture_recognition(up_fingers, list_lms):
    
    if(up_fingers == [4,8]):
        global click_down_flag, click_down_time
        x1, y1 = list_lms[4]
        x2, y2 = list_lms[8]
        res = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        
        if(res < 20):
            # try:
                if(click_down_flag == 0):
                    click_down_flag = 1
                    click_down_time = time.time()
                    print(f"按下：{res}")
                    return
            # except Exception as e:
            #     print(e)
        
                # 点击一秒后 转换为长按事件
                if(click_down_flag == 1 and time.time() - click_down_time > 1):
                    print("长按")
           
            #     pass
        else:
            # pass
            if(res > 100):
                if(click_down_flag == 1):
                    # click_up_flag = 1
                    print("抬起")
                    click_down_flag = 0

            # if(time.time() - click_time > 1000):
            #     pass


        # return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) 
    

# 初始化MediaPipe的手势识别模块  
mp_drawing = mp.solutions.drawing_utils  
mp_hands = mp.solutions.hands  
  
# 初始化摄像头  
cap = cv2.VideoCapture(0)  
  
with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7) as hands:  
    while cap.isOpened():  
        ret, image = cap.read()  
        if not ret:  
            print("Unable to receive frame.")  
            break  

        image_height, image_width, _ = np.shape(image)
  
        # 转换颜色空间：BGR到RGB  
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)  
        image.flags.writeable = False  

        # 进行手势识别  
        results = hands.process(image)  
  
        # 转换颜色空间回BGR  
        image.flags.writeable = True  
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

  
        # 绘制识别结果  
        if results.multi_hand_landmarks:  
            hand =results.multi_hand_landmarks[0]
            mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS)

            #采集所有关键点的坐标
            list_lms =[]
            for i in range(21):
                pos_x = hand.landmark[i].x*image_width
                pos_y= hand.landmark[i].y*image_height
                list_lms.append([int(pos_x),int(pos_y)])
            #构造凸包点
            list_lms = np.array(list_lms,dtype=np.int32)
            hull_index =[0,1,2,3,6,10,14,19,18,17,10]
            hull = cv2.convexHull(list_lms[hull_index,:])
            #绘制凸包
            cv2.polylines(image,[hull],True,(0,255,0),2)
            #查找外部的点数
            n_fig = -1
            ll = [4,8,12,16,20]
            up_fingers = []
            for i in ll:
                pt = (int(list_lms[i][0]),int(list_lms[i][1]))
                dist = cv2.pointPolygonTest(hull,pt,True)
                if dist < 0:
                    up_fingers.append(i)
            else:
                # 处理凸包外的点
                # print(up_fingers)
                # print(list_lms)
                gesture_recognition(up_fingers,list_lms)

            # for hand_landmarks in results.multi_hand_landmarks:  
            #     mp_drawing.draw_landmarks(  
            #         image, hand_landmarks, mp_hands.HAND_CONNECTIONS)  
  
        # 显示结果  
        cv2.imshow('MediaPipe Hands', image)  
  
        # 退出循环  
        if cv2.waitKey(5) & 0xFF == 27:  
            break  
  
cap.release()  
cv2.destroyAllWindows()

