import requests, re
import chardet
import csv, os
from datetime import datetime
from bs4 import BeautifulSoup
#import notify


# dictionary for currency name to search in the table, official name on the website
dic_for_coin = ['挪威克朗']
# dictionary for currency name to print in text
dic_for_prin_c = ['挪威元']
dic_for_info = ['现钞卖出价', '现汇卖出价']
dic_for_prin_i = ['现钞', '现汇']
dic_for_thre = [500, 500]

headertxt = '货币名称'
dic_for_info_index = []
dic_for_result = []
printres = ''

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}
headerrow = None
checkrows = []

if len(dic_for_coin) != len(dic_for_prin_c) or len(dic_for_info) != len(dic_for_prin_i):
    print('setting not valid, please check dic_for_coin align with dic_for_prin_c AND dic_for_info align with dic_for_prin_i')
    exit()

r = requests.get('https://www.boc.cn/sourcedb/whpj/', headers=headers)
if r.status_code == 200:
    detected_encoding = chardet.detect(r.content)['encoding']

    # Decode the content using the detected encoding
    content = r.content.decode(detected_encoding)
    #print(content)


    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')

    # Find the table rows (tr) in the HTML content
    rows = soup.find_all('tr')

    for row in rows:
        ths = row.find_all('th')
        for th in ths:
            if headertxt in th.text:
                headerrow = row
                break

    #print(headerrow)
    for info in dic_for_info:
        cells = headerrow.find_all('th')
        for i in range(len(cells)):
            if info in cells[i].text:
                dic_for_info_index.append(i)
    print(dic_for_info_index)

    # Iterate through the rows to find the one
    dic = dic_for_coin.copy()
    for row in rows:
        if not dic:
            break
        cells = row.find_all('td')
        for cell in cells:
            for check in dic:
                if check in cell.text:
                    checkrows.append(cells)
                    dic.remove(check)

    #print(dic)
    #print(dic_for_coin)

    for row in checkrows:
        res = []
        print(row)
        for ind in dic_for_info_index:
            #print(row[ind])
            cleaned_text = re.sub(r"</?td>", "", str(row[ind]))
            #print(cleaned_text)
            res.append(float(cleaned_text))
        dic_for_result.append(res)
    print(dic_for_result)

    if len(dic_for_coin) == len(dic_for_result) and len(dic_for_thre) == len(dic_for_result[0]):
        print('valid result')
        for i in range(len(dic_for_result)):
            for j in range(len(dic_for_result[i])):
                print(dic_for_coin[i] + ':\n' + dic_for_info[j] + ': ' + str(dic_for_result[i][j]))
                # generate csv file to log today's data for future use
                # Define the data you want to write or append to the CSV file
                file_path = dic_for_coin[i] + '_' + dic_for_info[j] + '.csv'
                # Check if the file exists
                file_exists = os.path.isfile(file_path)
                # Open the file in append mode
                with open(file_path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    # Write the data to the CSV file
                    writer.writerow([datetime.now().strftime('%Y-%m-%d'), dic_for_result[i][j]])

                # generate notify text
                if dic_for_result[i][j] < dic_for_thre[j]:
                    printres += (dic_for_prin_c[i] + '-' + dic_for_prin_i[j] + ':' + str(dic_for_result[i][j]) + '\n')

    print('====================================================================================')
    print(printres)
    if not printres.strip():
        print('发微信')
        #notify.send("今日汇率", context)

else:
    print("invalid request: " + r.text)
