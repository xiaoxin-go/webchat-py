from bs4 import BeautifulSoup
import re
# 读取xml文件
f = open('test.xml', encoding='utf-8')
text = f.read()
f.close()
soup = BeautifulSoup(text, 'xml')

# 获取所有包含快手号的节点
nodes = soup.find_all('node', {'text': re.compile(r'快手号: .*')})
print(nodes[0].get('text'))

# 根据resource-id获取快手号
node = soup.find('node', {'resource-id': 'com.smile.gifmaker:id/kwai_id_copy'})
print(node.get('text'))