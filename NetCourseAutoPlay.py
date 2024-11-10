from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime


def time_str_to_seconds(time_str):
    h, m, s = map(int, time_str.split(':'))
    return h * 3600 + m * 60 + s

account = ""
pword = ""
sburl = "https://www.shgb.gov.cn/djrck/reception/learningCenter"

def start_browser():
	driver = webdriver.Chrome()
	wait = WebDriverWait(driver, 2)
	# driver.maximize_window()
	driver.get(sburl)
	return driver, wait

def login(driver):
	driver.find_element(by=By.XPATH, value="/html/body/div[1]/div[1]/div/div[2]/div[2]/p").click()
	time.sleep(0.2)
	driver.find_element(by=By.XPATH, value='//*[@id="signupForm"]/input[1]').send_keys(account)
	driver.find_element(by=By.XPATH, value='//*[@id="dlPassword"]').send_keys(pword)
	driver.find_element(by=By.XPATH, value='//*[@id="btnSubmit"]').click() #登陆
	time.sleep(2)


def main_process():
	driver, wait = start_browser()
	try:
		login(driver)
		time.sleep(0.5)
		# driver.find_element(by=By.XPATH, value='').click()
		driver.find_element(by=By.XPATH, value='/html/body/div[1]/div[1]/div/div[2]/div[2]/p').click() 
		time.sleep(0.2)
		# assert len(driver.window_handles) == 1
		original_window = driver.current_window_handle
		driver.find_element(by=By.XPATH, value='//*[@id="spheader"]/div/ul/li[2]/a').click() 
		driver.find_element(by=By.XPATH, value='//*[@id="keyClassData"]/li/div[1]/a/img').click() 
		time.sleep(1.5)

		pageList = driver.find_element(by=By.XPATH, value='//*[@id="main"]/div[5]/div/div/div[2]/div/div/div[1]/div[2]/div[4]/div[2]/ul')
		pageButtons = pageList.find_elements(By.TAG_NAME, 'li')
		pageNum = len(pageButtons) - 2
		for pageIndex in range(1, pageNum + 1):
			processed_courses = set()
			courseDataList = driver.find_element(by=By.XPATH, value='//*[@id="courseData"]')
			courses = courseDataList.find_elements(By.TAG_NAME, 'li')

			for courseItem in courses:
				try:
				    course = courseItem.text
				    course_duration = time_str_to_seconds(course.split("课程时长：")[1].split("累计学习时长：")[0].strip())
				    learning_duration = time_str_to_seconds(course.split("累计学习时长：")[1].split("点击数：")[0].strip())
				    if course_duration > learning_duration:
				        watch_time = course_duration - learning_duration
				        hyperLinks = courseItem.find_elements(By.TAG_NAME, 'a')
				        for hl in hyperLinks:
				        	if hl.text in processed_courses:
				        		continue 

				        	print(f"正在学习课程:\"{hl.text}\", 课程时长：{course_duration}， 已学习时长：{learning_duration}, 还需学习: {watch_time} 秒。")
				        	print("")
				        	processed_courses.add(hl.text)
				        	hl.click()

				        	try:
					        	wait.until(EC.number_of_windows_to_be(2))
				        	except TimeoutException:
				        		print("登陆超时，系统发生错误，重新启动浏览器")
				        		driver.quit()
				        		return main_process()

				        	for window_handle in driver.window_handles:
				        		if window_handle != original_window:
				        			driver.switch_to.window(window_handle)
				        			time.sleep(watch_time)
				        			time.sleep(5)
				        			driver.close()
				        			break
				        	driver.switch_to.window(original_window)
				        	break

				except StaleElementReferenceException:
					print("元素失效，重新获取课程列表")
					courseDataList = driver.find_element(by=By.XPATH, value='//*[@id="courseData"]')
					courses = courseDataList.find_elements(By.TAG_NAME, 'li')
					continue  # 重新进入下一个课程项

			try:
				nextPageXpath = f'//*[@id="main"]/div[5]/div/div/div[2]/div/div/div[1]/div[2]/div[4]/div[2]/ul/li[{pageIndex + 1}]/a'
				# print(nextPageXpath)
				driver.find_element(by=By.XPATH, value=nextPageXpath).click()
				time.sleep(2)
			except NoSuchElementException:
				print("没有更多页面")
				break
	except Exception as e:
		print(f"程序遇到异常：{e}，正在退出")
		driver.quit()

main_process()

driver.quit()
