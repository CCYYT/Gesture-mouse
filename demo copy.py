import math
import time
import cv2  
import mediapipe as mp  
import numpy as np
import pyautogui 

import traceback # 打印错误堆栈信息

back_desk_flag = []

lock = 0
lock_time = 0

scroll_down_flag = []


click_down_flag = 0
click_up_flag = 0
click_down_time = 0
mouse_down = 0
mouse_axis = []
width = pyautogui.size().width
height = pyautogui.size().height
# up_fingers凸包外的点, list_lms所有点的坐标
def gesture_recognition(up_fingers, list_lms, list_lms_percentage):

    
    # 锁定/释放
    global lock, lock_time
    if(up_fingers != [] and up_fingers != [4,8,12,16,20] and lock == 1):
        return
    if(up_fingers == [4,8,12,16,20] and lock_time == 0):
        return
    if(up_fingers == []):
        if(lock_time == 0):
            lock_time = time.time()
        return
   
    elif(up_fingers == [4,8,12,16,20]):
        if(lock_time != 0):
            if(time.time() - lock_time < 1):
                if(lock == 0):
                    print("锁定")
                    lock = 1
                    lock_time = 0
                    return
                else:
                    print("解锁")
                    lock = 0
                    lock_time = 0
            else:
                lock_time = 0
    # print(up_fingers)

    # 移动鼠标
    if(up_fingers == [8]):
        pass
    # 点击/长按
    if(up_fingers == [4,8]):
        global click_down_flag, click_down_time, mouse_down, mouse_axis
        x1, y1 = list_lms[4]
        x2, y2 = list_lms[8]
        res = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        x_p, y_p = list_lms_percentage[4]
        x = (int)(width*x_p)
        y = (int)(height*y_p)
        try:
            if(mouse_axis == []):
                mouse_axis.append(x)
                mouse_axis.append(y)
            else:
                if(abs(mouse_axis[0] - x) > 25 or abs(mouse_axis[1] - y) > 25):
                    mouse_axis[0] = x
                    mouse_axis[1] = y
            pyautogui.moveTo(mouse_axis[0],mouse_axis[1])
        except Exception as e:
            print(e)
        if(res < 25):
            # try:
                if(click_down_flag == 0):
                    click_down_flag = 1
                    click_down_time = time.time()
                    print(f"左键按下")
                    pyautogui.mouseDown(button='left', x=None, y=None, duration=0.0)
                    # pyautogui.click()
                    return
            # except Exception as e:
            #     print(e)
        
                # 点击一秒后 转换为长按事件
                if(mouse_down == 0 and click_down_flag == 1 and time.time() - click_down_time > 1):
                    pyautogui.mouseDown(button='left', x=None, y=None, duration=0.0)
                    print("左键长按")
                    mouse_down = 1
           
            #     pass
        else:
            # pass
            if(res > 30):
                if(click_down_flag == 1):
                    # click_up_flag = 1
                    pyautogui.mouseUp(button='left', x=None, y=None, duration=0.0)
                    print("左键 抬起")
                    click_down_flag = 0
                    mouse_down = 0

            # if(time.time() - click_time > 1000):
            #     pass
    else:
        pyautogui.mouseUp(button='left', x=None, y=None, duration=0.0)
        click_down_flag = 0
        mouse_down = 0

    # 滚动
    # try:
    if(up_fingers == [4,8,12]):
        global scroll_down_flag
        x1, y1 = list_lms[4]
        x2, y2 = list_lms[8]
        x3, y3 = list_lms[12]
        res1 = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        res2 = math.sqrt((x3 - x1) ** 2 + (y3 - y1) ** 2)
        if(res1 < 25 and res2 < 30):
                if(scroll_down_flag == []):
                    scroll_down_flag = list_lms[4]
                    print("滚轮准备")
                else:
                    v = (int)((scroll_down_flag[0] - x1)*10)
                    if(v > 50 or v <-100):
                        pyautogui.scroll(v)
                        # print(list_lms[4],scroll_down_flag)
                        print(f"滚轮{v}")
                        if(v > 100 or v < -150):
                            scroll_down_flag = list_lms[4]
                    # pyautogui.scroll(10)
        
        else:
            if(res1 > 80 or res2 > 80):
                if(scroll_down_flag != []):
                    scroll_down_flag = []
                    print("滚轮 抬起")
    else:
        scroll_down_flag = []
    # except Exception as e:
    #     print(e)   
    #     traceback.print_exc() 
    

    # 回到桌面
    if(up_fingers == [8,12,16]):
        global back_desk_flag
        if(back_desk_flag == []):
            back_desk_flag = list_lms[4]
        else:
            x1, y1 = back_desk_flag
            x2, y2 = list_lms[4]
            res = y1 - y2
            if(res < -50):
                # 返回桌面
                pyautogui.hotkey('win', 'd')
                back_desk_flag = []

            if(res > 50):
                # 窗口切换
                pyautogui.hotkey('win', 'tab')
                back_desk_flag = []
    else:
        back_desk_flag = []



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
            list_lms_percentage = []
            for i in range(21):
                pos_x = hand.landmark[i].x*image_width
                pos_y= hand.landmark[i].y*image_height
                list_lms_percentage.append([hand.landmark[i].x,hand.landmark[i].y])
                list_lms.append([int(pos_x),int(pos_y)])
            #构造凸包点
            list_lms = np.array(list_lms,dtype=np.int32)
            hull_index =[0,1,2,3,6,9,13,18,17,10]
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
                gesture_recognition(up_fingers,list_lms,list_lms_percentage)

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

