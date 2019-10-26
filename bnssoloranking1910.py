import requests
import lxml.html as lh
import pandas as pd
import os
import math

# Constants
classdict = {'class1': '劍士', 'class2': '拳士', 'class3': '氣功士', 'class5': '力士', 'class6': '召喚師', 'class7': '刺客',
            'class8': '燐劍士', 'class9': '咒術師', 'class10': '乾坤士', 'class4': '槍擊士', 'class11': '鬥士', 'class12': '弓箭手'}
classAbbrdict = {'class1': 'BM', 'class2': 'KFM', 'class3': 'FM', 'class5': 'DES', 'class6': 'SUM', 'class7': 'ASS',
            'class8': 'BD', 'class9': 'WL', 'class10': 'SF', 'class4': 'GUN', 'class11': 'WD', 'class12': 'ARC'}
seasondict = {1: '第一週', 2: '第二週', 3: '第三週', 4: '第四週'}
url = 'http://tw.ncsoft.com/bns/event/1910/ranking/list'

# Get input variables
def errorInput():
    print("輸入格式錯誤，請重來！ Input format error, please retry")
    exit()

try:
    selWeek = int(input("輸入週次 Input Week [1-4]: "))
except ValueError:
    errorInput()
if(selWeek > 4 or selWeek < 1):
    errorInput()
try:
    selGameClass = int(input("輸入職業代碼 Input Class Code [0:ALL / 1:BM / 2:KFM / 3:FM / 4:GUN / 5:DES / 6:SUN / 7:ASS / 8:BD / 9:WL / 10:SF / 11:WD / 12:ARC]: "))
except ValueError:
    errorInput()
if(selGameClass > 12 or selGameClass < 0):
    errorInput()
if(selGameClass == 0):
    selGameClass = ""

page = requests.post(url, data = {'week': selWeek, 'gameclass': selGameClass})
doc = lh.fromstring(page.content)
tr_elements = doc.xpath('//tr')

# Get the header row of ranking table
for i in range(0, len(tr_elements)):
    row = tr_elements[i]
    for j in row.iterchildren():
        cell = j.text_content()
        if(cell == "角色名稱"):
            headerrow = i
            break

# Create an empty array
ranktable = []

# Parse table header
for cell in tr_elements[headerrow]:
    data = cell.text_content()
    ranktable.append((data,[]))
ranktable.append(("結算日期",[]))
ranktable.append(("週次",[]))

# Get latest update time & season
latesttime = 0
for i in range(headerrow + 1, len(tr_elements)):
    row = tr_elements[i]
    col = 0
    for cell in row.iterchildren():
        if col == 4:
            logtime = int(cell.text_content()[5:7] + cell.text_content()[8:10])
            if(logtime > latesttime):
                latesttime = logtime
        col += 1
#latesttime = 1024  # Override a custom latest time
latesttimestr = '2019.' + str(latesttime)[:2] + '.' + str(latesttime)[2:]
if(latesttime == 0):
    # No records
    print("沒有記錄 No records")
    exit()
else:
    seasonstr = seasondict[math.ceil((latesttime - 1016) / 7)]

# Parse table data
for i in range(headerrow + 1, len(tr_elements)):
    row = tr_elements[i]
    if len(row) != 5:
        break
    col = 0
    for cell in row.iterchildren():
        if col == 1:
            data = classdict[cell[0].get('class')]      
        else:
            data = cell.text_content()
        ranktable[col][1].append(data)
        col += 1
    ranktable[col][1].append(latesttimestr)
    ranktable[col+1][1].append(seasonstr)

Dict = {title:column for (title,column) in ranktable}
df = pd.DataFrame(Dict)

# Output
outputDir = os.path.dirname(__file__)
outputName = '/soloranking1910'
outputClass = ''
if(selGameClass != ""):
    outputClass = '_' + classAbbrdict['class' + str(selGameClass)]
outputNoHeader = '_noheader'
outputTimestamp = "_2019" + str(latesttime)
outputFormat = '.csv'
outputFileName = outputDir + outputName + outputClass + outputTimestamp + outputFormat
outputNHFileName = outputDir + outputName + outputClass + outputNoHeader + outputTimestamp + outputFormat
df.to_csv(outputFileName, index=None)
df.to_csv(outputNHFileName, index=None, header=None)

# Output preview in console
print("輸出預覽 Input Preview(只顯示前5行)")
print(df.head())
