import requests
from bs4 import BeautifulSoup
import xlwt
import re
import time
import random

book_name='房天下包头'

def request_fang(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    }
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response
    except requests.RequestException:
        return None


book = xlwt.Workbook(encoding='utf-8', style_compression=0)

sheet = book.add_sheet(book_name, cell_overwrite_ok=True)
sheet.write(0, 0, 'name')
sheet.write(0, 1, 'img')
sheet.write(0, 2, 'price')
sheet.write(0, 3, 'price_type')
sheet.write(0, 4, 'district')
sheet.write(0, 5, 'property_type')
sheet.write(0, 6, 'address')
sheet.write(0, 7, 'state')
sheet.write(0, 8, 'open_date')
sheet.write(0, 9, 'hand_date')
sheet.write(0, 10, 'property_type')
sheet.write(0, 11, 'developer')
sheet.write(0, 12, 'build_type')
sheet.write(0, 13, 'volume_ratio')
sheet.write(0, 14, 'green_rate')
sheet.write(0, 15, 'layout_info')

n = 1


def save_to_excel(soup):
    district_set={'朝阳','海淀','丰台','西城','东城','昌平','大兴','通州','房山','顺义','石景山','密云','门头沟','怀柔',
                  '延庆','平谷'}
    list = soup.find_all(class_="nlc_details")
    img_list=soup.find_all(class_="nlc_img")

    for i, item in enumerate(list):
        # img_url = img_list[i].find('a').find_all('img')
        # if len(img_url)==3:
        #     img_url=img_url[0].get('src')
        # else:
        #     img_url=img_url[1].get('src')
        img_url=img_list[i].a.find(class_='infbg').previous_sibling.previous_sibling.get('src')
        img_url='https:'+img_url

        item_name = item.find(class_='nlcd_name').a.string.strip()
        item_price = item.find(class_='nhouse_price').find('span')

        if item_price:
            item_price=item_price.text
        else:
            continue
        price_type=item.find(class_='nhouse_price').find('em')
        if price_type:
            price_type=price_type.text
        # 北京有span
        #district = item.find(class_='relative_message clearfix').find(class_='address').find('a').find('span')
        district = item.find(class_='relative_message clearfix').find(class_='address').find('a')
        if district:
            # district=district.string.strip()[1:-1]
            district = district.string
            district=re.search('.*?\[(.*)\]', district).group(1)
        else:
            print(item_name,'distirct')
            continue

        # if district not in district_set:
        #     continue

        s_url='https:'+item.find(class_='nlcd_name').a.get('href')
        s_html=request_fang(s_url)
        s_soup = BeautifulSoup(s_html.content, 'lxml', from_encoding='gb18030')

        link=s_soup.find(class_='mose_link')
        if link:
            detail_url='https:'+link.get('href')
        else:
            continue

        detail_html=request_fang(detail_url)
        if detail_html is None:
            continue
        d_soup = BeautifulSoup(detail_html.content, 'lxml', from_encoding='gb18030')

        info_list=d_soup.find_all(class_='list clearfix')
        main_info=info_list[0].find_all('li')
        property_type=main_info[0].find(class_='list-right').string.strip()
        build_type=main_info[2].find(class_='list-right').find('span').string.strip()
        build_type= re.sub(r'\s+',' ', build_type)
        # 北京索引不同
        developer=main_info[5].find(class_='list-right-text')
        if developer:
            if developer.find('a'):
                developer=developer.a.string
            else:
                developer='暂无资料'
        else:
            developer=main_info[5].find(class_='list-right').a.string
        # 北京索引不同
        address=main_info[6].find(class_='list-right-text')
        if address:
            address=address.string.strip()
        else:
            address=main_info[6].find(class_='list-right').string.strip()

        selling_info=info_list[1].find_all('li')
        state=selling_info[0].find(class_='list-right').string.strip()
        open_date=selling_info[2].find(class_='list-right').text[:-8]
        hand_date=selling_info[3].find(class_='list-right')
        if hand_date.a:
            hand_date=hand_date.text[:-len(hand_date.a.text)]
        else:
            hand_date=hand_date.text

        community_info=d_soup.find(class_='clearfix list').find_all('li')
        volume_ratio=community_info[2].find(class_='list-right').string
        green_rate=community_info[3].find(class_='list-right').string

        layout_info=[]
        layout_url=d_soup.find(class_='cxfnav')
        if layout_url:
            layout_url=layout_url.find_all('a')[3]
            if layout_url.text=='户型':
                layout_url='https:'+layout_url.get('href')
            else:
                continue
        else:
            continue
        layout_html = request_fang(layout_url)
        layout_soup = BeautifulSoup(layout_html.content, "html.parser",from_encoding='gb18030')
        layout_list=layout_soup.find(class_='xc_list').find('ul').find_all('li')
        if len(layout_list)==0:
            continue
        for info in layout_list:
            layout_name=info.find('a').find('p').find('span').text
            tmp=info.find(class_='tiaojian').a
            layout=tmp.find(class_='fl').string
            area=tmp.find(class_='fr').string.strip()
            area = re.sub(r'\s+', ' ', area)
            layout_info.append(str(layout_name)+','+str(layout)+','+str(area))
        layout_info=';'.join(layout_info)
        #item_name=soup.select('.nlcd_name a')
        # item_img = item.find('a').find('img').get('src')
        # item_index = item.find(class_='').string
        # item_score = item.find(class_='rating_num').string
        # item_author = item.find('p').text
        # if (item.find(class_='inq') != None):
        #     item_intr = item.find(class_='inq').string

        print(item_name)
        global n
        sheet.write(n, 0, item_name)
        sheet.write(n, 1, img_url)
        sheet.write(n, 2, item_price)
        sheet.write(n, 3, price_type)
        sheet.write(n, 4, district)
        sheet.write(n, 5, property_type)
        sheet.write(n, 6, address)
        sheet.write(n, 7, state)
        sheet.write(n, 8, open_date)
        sheet.write(n, 9, hand_date)
        sheet.write(n, 10, property_type)
        sheet.write(n, 11, developer)
        sheet.write(n, 12, build_type)
        sheet.write(n, 13, volume_ratio)
        sheet.write(n, 14, green_rate)
        sheet.write(n, 15, layout_info)

        n = n + 1


def main(i):
    # url = 'https://newhouse.fang.com/house/s/b9'+str(1+i)+'/'
    url = 'https://bt.newhouse.fang.com/house/s/b9' + str(1 + i) + '/'
    html = request_fang(url)
    soup = BeautifulSoup(html.content, 'lxml',from_encoding='gb18030')
    save_to_excel(soup)
    sleep_time=random.uniform(0.5,1.5)
    time.sleep(sleep_time)


if __name__ == '__main__':
    #url = 'https://newhouse.fang.com/house/s/'
    url = 'https://bt.newhouse.fang.com/house/s/'
    html = request_fang(url)
    soup = BeautifulSoup(html.content, 'lxml', from_encoding='gb18030')
    last_page = soup.select('.last')
    page_number = int(last_page[0]['href'].split('/')[3].split('9')[1])  # 根据尾页划分页码
    for i in range(0,page_number):
        print(i)
        main(i)

book.save(u'房天下包头.xls')
