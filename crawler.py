from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.request
from dotenv import load_dotenv
import time
import random
import os


'''
문제 발생 시 debug_check_point 부분 확인
'''

def check_assignments():
    options = Options()
    options.add_argument('--headless') #headless모드 브라우저가 뜨지 않고 실행됩니다.
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("detach", True)
    options.add_argument('--start-maximized')
    #options.add_argument("--disable-blink-features=AutomationControlled")

    # User-Agent 설정
    user_agent = "	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")

    driver = webdriver.Chrome(options=options)

    print("시작")

    '''
    1. 학교 홈페이지 로그인
    '''
    #학교 LMS 로그인 페이지 접속
    #############   debug_check_point_00. 학교 홈페이지 접속 불가(ip 차단)   ###########
    driver.get("https://lms.ssu.ac.kr/login")
    print("학교 로그인 페이지 접속")
    time.sleep(random.uniform(2,4))


    # 아이디와 비밀번호 입력 (form 태그 안의 input 요소를 선택)
    load_dotenv()
    my_id = os.getenv("SSU_ID") #내 id
    my_pw = os.getenv("SSU_PW") #내 pw

    if my_id is None or my_pw is None:
        print("환경 변수 안 불러와짐")


    # 아이디 입력: name="userid", id="userid"
    username_input = driver.find_element(By.ID, "userid")
    username_input.clear()  # 혹시 기존 값이 있다면 지우기
    username_input.send_keys(my_id)  

    time.sleep(random.uniform(1,2))

    # 비밀번호 입력: name="pwd", id="pwd"
    password_input = driver.find_element(By.ID, "pwd")
    password_input.clear()
    password_input.send_keys(my_pw)  

    time.sleep(random.uniform(1,2))

    # 로그인 버튼 클릭
    # 3-1. 로그인 버튼은 <a> 태그로 되어 있으며, 클래스가 "btn_login" 입니다.
    login_button = driver.find_element(By.CSS_SELECTOR, "a.btn_login")
    login_button.click()
    print("로그인 ok")

    # # 로그인 버튼 클릭
    # # 3-2. 버튼이 <a> 태그로 되어 있어, 자바스크립트 실행해야 할 가능성이 있음.
    # # login_button = driver.find_element(By.CLASS_NAME, "btn_login")
    # # driver.execute_script("arguments[0].click();", login_button)  # JavaScript 클릭 실행

    time.sleep(random.uniform(13,15)) # 로그인 후 페이지 로딩 대기

    '''
    2. 마이페이지 이동 -> 과제 및 퀴즈 정보 스크래핑
    '''

    # 마이페이지 이동
    driver.get("https://lms.ssu.ac.kr/mypage")
    print("마이페이지 이동")
    time.sleep(random.uniform(8,11))

    # 내가 원하는 정보가 iframe 안에 있음
    # 2. iframe 태그 찾기
    iframe = driver.find_element(By.CSS_SELECTOR, "iframe#fulliframe")  # iframe id

    # 3. 해당 iframe 안으로 전환
    driver.switch_to.frame(iframe)

    # 4. iframe 안에서 원하는 요소 크롤링
    soup = BeautifulSoup(driver.page_source, "html.parser")
    #print(soup)

    course_container = soup.find_all( attrs={'class':'xn-student-course-container'} )
    #print(course_container)

    '''
    3. 크롤링해온 요소에서 필요한 부분 추출하여 result 생성
    result = [
        {course_title: "",
            todos: [
                {
                    todo_title: "",
                    todo_count: 0
                },
                {
                    todo_title: "",
                    todo_count: 1
                },
            ]
        }, 
    ]
    '''
    # result 배열 생성
    result = []

    for element in course_container:
        # 과목 이름
        course_title_tag = element.find("p", class_="xnscc-header-title")
        course_title = course_title_tag.text.strip() if course_title_tag else "없음"
        print(course_title)
        todos = []
        # 각각의 todo divs
        todo_count_divs = element.find_all("div", class_="xn-todo-count")

        for div in todo_count_divs:        
            #내가 확인할 todo title
            requirements = ["동영상", "과제", "퀴즈"]
            
            # todo title
            todo_title_tag = div.find("span", class_="xntc-title")
            #############   debug_check_point_01. todo title이 "없음"일 경우 코드 수정 필요(스크래핑 과정에서의 문제)   ###########
            todo_title = todo_title_tag.text.strip() if todo_title_tag else "없음"
            print(f"📌todo_title: {todo_title}")
            if(todo_title not in requirements):
                print("⛔ 조건 불만족: 요구사항에 없는 항목")
                continue

            # todo count
            todo_count_tag = div.find("a", class_="xntc-count")
            if todo_count_tag:
                print(f" 📥 todo_count raw: {todo_count_tag.text.strip()}")
            else:
                print(" ❌ todo_count_tag 없음")
            #############   debug_check_point_02. todo count가 -1일 경우 코드 수정 필요(스크래핑 과정에서의 문제)   ###########
            todo_count = int(todo_count_tag.text.strip()) if todo_count_tag and todo_count_tag.text.strip().isdigit() else -1
            if(todo_count != 1):
                print(" ⚠️ todo_count 조건 불만족 (todo_count != 1)")
                continue
            
            print("todo에 추가됨")
            todos.append({
                "todo_title": todo_title,
                "todo_count": todo_count
            })
        if todos:
            result.append({
                "course_title": course_title,
                "todos": todos
            })

    driver.switch_to.default_content()

    driver.quit()

    print(result)
    return result
