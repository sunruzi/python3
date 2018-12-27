#功能：爬取固定资产与房地产两个父指标下，所有子指标里所有省市自2013年以后的数据
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd

js = '''$(\".experience\").hide();'''
AREAS = ['110000', '120000', '130000', '140000', '150000', '210000', '220000', '230000', '310000', '320000', '330000', '340000', '350000', '360000', '370000',
         '410000', '420000', '430000', '440000', '450000', '460000', '500000', '510000', '520000', '530000', '540000', '610000', '620000', '630000', '640000', '650000']
FATHERPOINTS = ['treeZhiBiao_6_a', 'treeZhiBiao_7_a']
SONPOINTS1 = ['treeZhiBiao_9', 'treeZhiBiao_10', 'treeZhiBiao_11']
SONPOINTS2 = ['treeZhiBiao_9', 'treeZhiBiao_10', 'treeZhiBiao_11', 'treeZhiBiao_12', 'treeZhiBiao_13']
tree1 = [FATHERPOINTS[0], SONPOINTS1, AREAS]
tree2 = [FATHERPOINTS[1], SONPOINTS2, AREAS]
TargetPath = [tree1, tree2]
print(tree2)
print(TargetPath)

def source_code(fatherPoint, sonPoint, areaCode):
    chrom_options = Options()
    chrom_options.add_argument('--headless')
    chrom_options.add_argument('--no-sandbox')
    chrom_options.add_argument('--disable-dev-shm-usage')
    chrom_options.add_argument('--disable-gpu')
    # browser = webdriver.Chrome()
    # 此处下载71.0.3578.80版本32位谷歌浏览器及驱动
    browser = webdriver.Chrome(chrome_options=chrom_options)
    try:
        browser.get('http://data.stats.gov.cn/easyquery.htm?cn=E0101')
        browser.maximize_window()
        locator = (By.XPATH, '//div[@class="mr-content"]')
        WebDriverWait(browser, 20, 0.5).until(
        EC.presence_of_element_located(locator))
        sleep(1)
        browser.execute_script(js)
        with open('f.html', 'w') as f:
            f.write(browser.page_source)
        browser.find_element(
            By.XPATH, '//a[@id="{}"]'.format(fatherPoint)).click()
        sleep(1)
        #切换页面
        browser.switch_to.window(browser.window_handles[0])
        browser.find_element(
            By.XPATH, '//li[@id="{}"]'.format(sonPoint)).click()

        browser.find_element(
            By.XPATH, '//div[@id="mySelect_reg"]/div[@class="dtHtml"]/div[@class="dtHead"]').click()
        with open('f.html', 'w') as f:
            f.write(browser.page_source)
        browser.find_element(
            By.XPATH, '//div[@id="mySelect_reg"]/div[@class="dtHtml"]/div[@class="dtBody"]/div[@class="dtList"]/ul/li[@code="{}"]'.format(areaCode)).click()
        browser.find_element(
            By.XPATH, '//div[@id="mySelect_sj"]/div[@class="dtHtml"]/div[@class="dtHead"]').click()
        browser.find_element(
            By.XPATH, '//div[@id="mySelect_sj"]/div[@class="dtHtml"]/div[@class="dtBody"]/div[@class="dtFoot"]/input[@class="dtText"]').send_keys("2013-2017")
        browser.find_element(By.XPATH, '//div[@class="dtTextBtn"]').click()
        sourceCode = browser.page_source
        browser.quit()
        return sourceCode
    finally:
        browser.quit()

def annalysis_source_code(source_code, sonPoint):
    global name
    soup = BeautifulSoup(source_code, 'lxml')
    # 此处测试中文乱码问题解决情况
    # print(soup.originalEncoding)
    # print(soup.prettify())
    region = soup.select(
        'div[id="mySelect_reg"] > div[class="dtHtml"] > div[class="dtHead"]')[0].get_text()
    print(region)
    name = soup.select('li[id="{}"] > a'.format(sonPoint))[0].get("title")
    headers = []
    headerArr = soup.select(
        'table[class="public_table table_fix"] > thead > tr[class="tr-title"] > th')
    for i in headerArr:
        headers.append(i.span['code'])
    tables = []
    rowArr = soup.select('table[class="public_table table_fix"] > tbody > tr')
    for rowSoup in rowArr:
        blocks = []
        row = rowSoup.select('td')
        for i in row:
            blocks.append(i.get_text())
        tables.append(blocks)
    df = pd.DataFrame(tables, columns=headers)
    df = df.T
    columnName = df.ix['zb'].values.tolist()
    df.columns = columnName
    df = df.drop(['zb'])
    df['region'] = region

    # df.to_csv('{}.csv'.format(region))
    return df

name = ''
print(name)
for tree in TargetPath:
    fatherPoint = tree[0]
    sonPoints = tree[1]
    areas = tree[2]
    for sonPoint in sonPoints:
        dfs = []

        for area in areas:
            print('Now loading:{}-{}-{}'.format(fatherPoint, sonPoint, area))
            sourceCode = source_code(fatherPoint, sonPoint, area)
            df = annalysis_source_code(sourceCode, sonPoint)
            dfs.append(df)
            print('--------{} LOADED--------'.format(area))
        result = pd.concat(dfs)
        # pd写入csv解决中文乱码
        result.to_csv('{}.csv'.format(name), encoding="utf_8_sig")