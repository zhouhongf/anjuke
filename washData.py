import re


start_urls = set()
file = open('citylinks_last_page.txt')
links = file.readlines()
for link in links:
    temp_link = link[:-1]
    result = re.match('(.*)p50/', temp_link)
    if result is not None:
        start_urls.add(result.group(1))
file.close()

with open('citylinkmore.txt', 'a') as f:
    for url in start_urls:
        the_url = url + '\n'
        f.writelines(the_url)
