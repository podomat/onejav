#-*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoAlertPresentException

from bs4 import BeautifulSoup
import datetime
import sys
import random
from time import sleep
import urllib
import re
import os
import db
import MySQLdb


class OnejavTorrentTrawler:
	# 생성자
	def __init__(self):
		self.webdriver_path = '..\chromedriver\chromedriver'
		self.fireofx_driver_path = 'C:\eData\geckodriver\geckodriver'
		self.url_prefix = 'https://onejav.com'
		self.data_dir = '../onejav_data/'

	# 소멸자
	def __del__(self):
		if(self.driver != None):
			self.driver.close()
		#self.close_log()
		
	
	# 웹 드라이버 초기화
	def init_driver(self, browser):
		self.browser_name = browser
		if(browser == 'chrome'):
			options = webdriver.ChromeOptions()
			options.add_argument('headless')
			
			'''
			크롬 로그 레벨			
			- INFO = 0, 
			- WARNING = 1, 
			- LOG_ERROR = 2, 
			- LOG_FATAL = 3.
			- default is 0.
			'''
			options.add_argument('log-level=1')
			options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images":2})
			self.driver = webdriver.Chrome(self.webdriver_path, chrome_options=options)
			self.driver.set_window_size(1280, 960)
		
		elif(browser == 'firefox'):
			options = webdriver.FirefoxOptions()
			options.add_argument('-headless')
			self.driver = webdriver.Firefox(executable_path=self.fireofx_driver_path, firefox_options=options)
			
		self.driver.implicitly_wait(5)
		
	
	# 품번 형식 구성
	def make_poombun_format(self, str):
		p = re.compile('[0-9]+')
		pos = p.search(str).span()[0]
		return (str[:pos] + '-' + str[pos:]).lower()
		
		
	# 일별 파일 저장 디렉토리 생성
	def make_dir(self, date):
		dname = self.data_dir + re.sub('/', '', date)
		if not os.path.exists(dname):
			os.makedirs(dname)
		return dname

		
	
	# maker를 기존 이름으로 변환
	def convert_maker(self, maker):
		maker_dic = {
			'プレステージ' : 'PRESTIGE',
			'BLACK＆BLACK' : 'BLACK&BLACK',
			'サディスティックヴィレッジ' : 'SOD',
			'SODクリエイト':'SOD',
			'アイエナジー': 'IEnergy',
			'アイデアポケット': 'IdeaPocket',
			'オーロラプロジェクト・アネックス': 'AuroraProject',
			'ケイ・エム・プロデュース': 'KMP',
			'センタービレッジ': 'CenterVillage',
			'ながえスタイル': 'ながえSTYLE',
			'マックスエー':'MAX-A',
			'ムーディーズ': 'MOODYZ',
			'ワンズファクトリー': 'WANZ',
			'Prestige': 'PRESTIGE',
			'グローリークエスト': 'GloryQuest',
			'ナチュラルハイ':'NaturalHigh',
			'美':'痴女ヘブン',
			'F＆A': 'SOD',
			'h.m.pDORAMA': 'h.m.p',
			'ヴィ':'V',
			'ヒビノ': 'HIBINO',
			'ルビー': 'RUBY',
			'GIGOLO（ジゴロ）': 'GIGOLO',
			'ケー・トライブ':'K-Tribe',
			'MERCURY（マーキュリー）': 'MERCURY',
			'U＆K': 'U&K',
			'バミューダ': 'BERMUDA',
			'シャーク': 'Shark',
			'オペラ': 'OPERA',
			'レッド': 'RED',
			'ゴールデンタイム':'GoldenTime',
			'マキシング':'MAXING',
			'アパッチ（デマンド）': 'Apache',
			'ディープス': 'DEEP\'S',
			'マドンナ': 'Madonna',
			'ピーターズMAX':'ピーターズ',
			'FAプロ・プラチナ':'FAプロ',
			'M男パラダイス':'M男Paradise',
			'アリスJAPAN':'AliceJapan',
			'ビッグモーカル':'BigMorkal',
			'ブイアンドアールプロデュース':'V&R',
			'エムズビデオグループ':'M\'s',
			'ホットエンターテイメント':'HOT',
			'ブリット':'BULLITT',
			'グローバルメディアエンタテインメント':'Global',
			'ワープエンタテインメント':'WAAP',
			'プラネットプラス': 'PLANETPLUS',
			'ドリームチケット': 'DreamTicket',
			'アートモード': 'ArtMode',
			'アタッカーズ': 'ATTACKERS',
			'エスワン ナンバーワンスタイル':'S1',
			'プレミアム':'PREMIUM',
			'ドグマ': 'Dogma',
			'コスモス映像': 'COSMOS',
			'マッド（月）': 'MAD'
		}
		
		if maker in maker_dic:
			maker = maker_dic[maker]
		
		return re.sub(' ','',maker)
		
		
	def get_kor_name_from_hentaku(self, jpn_name):
		base_url = 'https://google.com/ncr'
		
		self.driver.get(base_url)
		self.driver.find_element_by_id('lst-ib').send_keys(jpn_name + ' site:hentaku.net')
		button = self.driver.find_element_by_xpath('//*[@id="tsf"]/div[2]/div[3]/center/input[1]')
		self.driver.execute_script("arguments[0].click();", button)
		
		html = self.driver.page_source
		soup = BeautifulSoup(html, 'html.parser')
		
		title = soup.find('h3', {'class':'r'})
		if(title == None): return None
		
		title = title.get_text()
		print ('[Google search result]: {0} -> {1}'.format(jpn_name, title))
		
		pos = title.find('/')
		if(pos < 0): return None
		
		kor_name = title[:pos-1]
		return kor_name
		
		
	def get_kor_name(self, jpn_name):
		ojdb = db.OnejavDB()
		kor_name = ojdb.get_kor_name(jpn_name)
		
		'''
		if(kor_name == None):
			kor_name = self.get_kor_name_from_hentaku(jpn_name)
			if(kor_name == None):
				ojdb.insert_jpn_name(jpn_name)
			else:
				ojdb.insert_name_pair(jpn_name, kor_name)
		'''
		if(kor_name == None):
			ojdb.insert_jpn_name(jpn_name)
		
		return kor_name
		
		
		
	# 상세 정보 수집
	def get_jav_info(self, poombun):
		page_address = False
		actresses = ''
		#javlib_url = 'http://www.w24j.com/ja/'
		javlib_base_url = 'http://www.d28k.com/ja/'
		javlib_url = javlib_base_url

		if (poombun[:7] == 'http://' or poombun[:8] == 'https://'):
			page_address = True
			javlib_url = poombun

		self.driver.get(javlib_url)

		if (page_address == False):
			self.driver.find_element_by_id('idsearchbox').send_keys(poombun)
			button = self.driver.find_element_by_xpath('//*[@id="idsearchbutton"]')
			self.driver.execute_script("arguments[0].click();", button)
		
		html = self.driver.page_source
		soup = BeautifulSoup(html, 'html.parser')

		#print (soup)
		if soup.find('div', {'id':'video_title'}) == None:
			found = False
			print(' There is no video_title.')
			vth_list = soup.find('div', {'class':'videothumblist'})
			if vth_list == None:
				print(' There is no videothumblist.')
				return None, None, None, None, None

			video_list = vth_list.find('div', {'class':'videos'}).find_all('div', {'class':'video'})
			if video_list == None:
				print(' There is no videos.')
				return None, None, None, None, None

			if video_list == None:
				print(' There is no video list.')
				return None, None, None, None, None

			for video in video_list:
				title = video.find('a')['title']
				if title == None:
					print(' There is no title.')
				
				if title.find('ブルーレイディスク') == -1 :
					print(' Found not bluelay disk.')
					javlib_url = javlib_base_url + video.find('a')['href'][2:]
					if javlib_url == None :
						print(' There is no href.')
						return None, None, None, None, None
					self.driver.get(javlib_url)
					html = self.driver.page_source
					soup = BeautifulSoup(html, 'html.parser')
					found = True
					break

			if found == False:
				print(' There is bluelay disk only.')
				return None, None, None, None, None

		jacket_url = soup.find('div', {'id':'video_jacket'}).find('img')['src']
		if jacket_url[:2] == '//':
			jacket_url = 'http:' + jacket_url
		#jacket_url = jacket_url.find('img')['src']

		if (page_address == True):
			poombun = soup.find('div', {'id':'video_id'}).find_all('td')[1].get_text().strip().lower()
		
		maker = soup.find('div', {'id':'video_maker'})
		if (maker == None):
			return None, None, None, None, None
			
		maker = maker.find('td', {'class':'text'}).get_text().strip()
		rel_date = soup.find('div', {'id':'video_date'}).find('td', {'class':'text'}).get_text().strip()

		actress_list = soup.find('div', {'id':'video_cast'}).find_all('span', {'class':'star'})
		if(actress_list != None):
			index = 0
			for actress in actress_list :
				index = index + 1
				if(index > 1):
					actresses = actresses + ', '
				actress_name = actress.get_text()
				kor_name = self.get_kor_name(actress_name)
				if (kor_name != None):
					actress_name = actress_name + ' ' + kor_name
				actresses = actresses + actress_name
				if(index >= 12): break
		
		rel_date = re.sub('-', '', rel_date)
		maker = re.sub('/.*$', '', maker)
		
		return rel_date, maker, actresses, jacket_url, poombun
		
		
	def check_alert_and_cancel(self):
		try:
			alert = self.driver.switch_to_alert()
			if(alert != None):
				self.comment_alert = alert.text.strip()
				print('   >> Alert: {0}'.format(self.comment_alert))
				alert.dismiss()
				return True
		except NoAlertPresentException as e:
			pass
		except Exception as e:
			print('Exception: {0}'.format(e))
		
		return False
		
		
	# 일별 torrent ripping
	def run_ripping(self, date, check):
		page = 0
		completed = False
		directory = self.make_dir(date)
		
		while completed == False:
			page = page + 1
			list_url = '{0}/{1}?page={2}'.format(self.url_prefix, date, page)
			print('   >> Page {0}: {1}'.format(page, list_url))
	
			self.driver.get(list_url)
			self.check_alert_and_cancel()
			html = self.driver.page_source
			soup = BeautifulSoup(html, 'html.parser')
			jav_list = soup.find_all('div', {'class':'card mb-3'})
			if(len(jav_list)==0):
				print('   >> There is no div(class=card mb-3) list')
				break
			
			index = 0
			for jav in jav_list:
				index = index + 1
				poomsize = jav.find('h5', {'class':'title is-4 is-spaced'})
				poombun = self.make_poombun_format(poomsize.find('a').get_text().strip())
				filesize = poomsize.find('span').get_text().strip()
				print('[{0}-{1}-{2}] {3}({4})'.format(date, page, index, poombun, filesize))
				rel_date, maker, actresses, notused1, notused2 = self.get_jav_info(poombun)
				if(rel_date == None):
					filename = poombun
				else:
					maker = self.convert_maker(maker)
					if(actresses == ''):
						filename = '{0} {1} {2}'.format(maker, poombun, rel_date)
					else:
						filename = '{0} {1} {2} {3}'.format(maker, poombun, rel_date, actresses)
				
				# 배우 DB 업데이트만 할 때는 여기까지만 수행
				if (check == True): continue
				
				# 이미지 파일 다운로드
				img_fname = '{0}/{1}.jpg'.format(directory, filename)
				if (os.path.isfile(img_fname) == False):
					img_url = jav.find('img', {'class':'image'})['src']
					#print('image link: {0}'.format(img_url))
					while True:
						retry_count = 0
						try:
							urllib.request.urlretrieve(img_url, img_fname)
						except Exception as e:
							print (e)
							sleep(3)
							retry_count = retry_count + 1
							if (retry_count < 3):
								continue
						break

				# 토렌트 파일 다운로드
				tor_fname = '{0}/{1}({2}).torrent'.format(directory, filename, filesize)
				if (os.path.isfile(tor_fname) == False):
					tor_url = self.url_prefix + jav.find('a', {'title':'Download .torrent'})['href']
					#print('torrent link: {0}'.format(tor_url))
					while True:
						retry_count = 0
						try:
							#print('다운로드 시도: {} -> {}'.format(tor_url, tor_fname))
							urllib.request.urlretrieve(tor_url, tor_fname)
							#print('wget.download: {0}'.format(tor_url))
							#wget.download(tor_url, tor_fname)
						except Exception as e:
							print ('Exception: {}'.format(e))
							sleep(3)
							retry_count = retry_count + 1
							if (retry_count < 3):
								continue
						break
				

			page_navi = soup.find('ul', {'class':'pagination-list'})
			if(page_navi != None):
				li_list = page_navi.find_all('li')
				li_count = len(li_list)
				last_page = int(li_list[li_count-1].find('a').get_text())
				print('   >> Last page: {0}'.format(last_page))
				if (last_page <= page):
					print('   >> Ripping completed.')
					break
			else:
				print('   >> There is no page navigation, Ripping completed.')
				break

	def get_video_jacket(self, poombun):
		poombun = poombun.lower()

		rel_date, maker, actresses, jacket_url, poombun = self.get_jav_info(poombun)
		if rel_date == None:
			print('Unknown poombun: {0}'.format(poombun))
			return

		maker = self.convert_maker(maker)
		if(actresses == ''):
			filename = '{0} {1} {2}'.format(maker, poombun, rel_date)
		else:
			filename = '{0} {1} {2} {3}'.format(maker, poombun, rel_date, actresses)

		# 이미지 파일 다운로드
		img_fname = '{}.jpg'.format(filename)
		if (os.path.isfile(img_fname) == False):
			while True:
				retry_count = 0
				try:
					urllib.request.urlretrieve(jacket_url, img_fname)
				except Exception as e:
					print (e)
					sleep(3)
					retry_count = retry_count + 1
					if (retry_count < 3):
						continue
				break


def show_help():
	print('Usage: {0} <command> [<date>]'.format(sys.argv[0]))
	print('   <command> :')
	print('      - f <yyyy/mm/dd>: find out about actress''s name')
	print('      - s <yyyy/mm/dd>: download seeds and posters')
	print('      - p <sam-572 | http://www.d28k.com/ja/...>: download poster')				


if __name__ == '__main__':
	date = '2018/06/01'
	browser = 'chrome'
	check = False
	#browser = 'firefox'
	
	# test code
	'''
	ojtt = OnejavTorrentTrawler()
	ojtt.init_driver(browser)
	kname = ojtt.get_kor_name_from_hentaku('永嶋輝子')
	print (kname)
	sys.exit(0)
	'''
	# test code
	
	if len(sys.argv) != 3:
		show_help()
		sys.exit(0)

	if sys.argv[1] == 'f':
		check = True
		date = sys.argv[2]
	elif sys.argv[1] == 's':
		check = False
		date = sys.argv[2]
	elif sys.argv[1] == 'p':
		poombun = sys.argv[2]
	else: 
		show_help()
		sys.exit(0)
		
	ojtt = OnejavTorrentTrawler()
	print('Onejav trawlBot instance created.')
	ojtt.init_driver(browser)
	print('({0}) driver initialized.'.format(browser))
	
	if sys.argv[1] == 'f' or sys.argv[1] == 's':
		ojtt.run_ripping(date, check)
	else :
		ojtt.get_video_jacket(poombun)
	


