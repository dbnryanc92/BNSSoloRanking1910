import requests
import lxml.html as lh
import pandas as pd
import os
import math

# Constants
classdict = {'class1': '劍士', 'class2': '拳士', 'class3': '氣功士', 'class5': '力士', 'class6': '召喚師', 'class7': '刺客',
            'class8': '燐劍士', 'class9': '咒術師', 'class10': '乾坤士', 'class4': '槍擊士', 'class11': '鬥士', 'class12': '弓箭手'}
seasondict = {1: '第一週', 2: '第二週', 3: '第三週', 4: '第四週'}

# Input
url = 'http://tw.ncsoft.com/bns/event/1910/ranking/list'
selWeek = "2"  # Week: 1 - 4
selGameClass = ""  # Class: 1 - 12, Refer to classdict

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
latesttime = 1016
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
#print(latesttime)
latesttimestr = '2019.' + str(latesttime)[:2] + '.' + str(latesttime)[2:]
seasonstr = seasondict[math.ceil((latesttime - 1016) / 7)]
#print(seasonstr)

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
            #if col == 4:
                
            data = cell.text_content()
        ranktable[col][1].append(data)
        col += 1
    ranktable[col][1].append(latesttimestr)
    ranktable[col+1][1].append(seasonstr)

Dict = {title:column for (title,column) in ranktable}
df = pd.DataFrame(Dict)

outputDir = os.path.dirname(__file__)
outputName = '/soloranking1910'
outputNoHeader = '_noheader'
outputTimestamp = "_2019" + str(latesttime)
outputFormat = '.csv'
df.to_csv(outputDir + outputName + outputTimestamp + outputFormat, index=None)
df.to_csv(outputDir + outputName + outputNoHeader + outputTimestamp + outputFormat, index=None, header=None)

# output preview
print(df.head())
