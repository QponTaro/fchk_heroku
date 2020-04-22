# 日付操作系 ライブラリ
import time
import datetime
from dateutil.relativedelta import relativedelta

# WebDriver系
# from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# import chromedriver_binary  # Adds chromedriver binary to path

from bs4 import BeautifulSoup

import subs.datesub as datesub

# data, 辞書 インポート
# import data.data as data
import data.data as dic
from data.data import room_data, room_datum
from data.data import chk_datum
# from data.data import chk_date, chk_datum

# ---------------------------------
# 空きを確認する 日付リストを作成する
# ※使用中
# ---------------------------------


def make_chk_date_list():

    # 今日の日付を取得
    today = datetime.datetime.now()

    # 【開始日】
    #  今日の翌々月1日
    date_from = (today + relativedelta(months=2)).replace(day=1)

    # 【終了日】
    # 23日-30/31までは、４か月後の月末
    # 1日～28日までは 3カ月後の月末

    if today.day >= 16:  # 今日が 16日～月末
        addMonth = 4
    else:                # 今日は 1~15日
        addMonth = 3

    # date_to = (today + relativedelta(months=addMonth)
    #             ).replace(day=1) - datetime.timedelta(days=1)
    # dt = date.today() + relativedelta(years=1, months=1, day=1, days=-1)
    date_to = today + relativedelta(months=addMonth + 1, day=1, days=-1)
    # date_to = (today + relativedelta(months=addMonth))

    print('chk {} ~ {}'.format(date_from, date_to))

    lst = []
    for room in dic.check_ROOMs:

        # === 日付ループ ===
        t = date_from
        while t <= date_to:

            curWeek = datesub.get_weekstr(t.year, t.month, t.day)
            curHoliday = datesub.chk_holiday(t.year, t.month, t.day)

            # 土日祝 以外は対象外
            if ((curWeek in {"土", "日"}) or (curHoliday is not None)):

                lst.append(chk_datum(t.year, t.month, t.day, curWeek, room))

            t += datetime.timedelta(days=1)

    return lst

# 今使っている関数


# ---------------------------------
# 日付リスト に従い チェックする
# ※使用中
# ---------------------------------
def chk_free_room_bs(self, lst):
    result_msg = ""

    lstRoom = ""
    for tgt in lst:

        # 施設指定
        curRoom = tgt.room
        curYear = tgt.year
        curMonth = tgt.month
        curDay = tgt.day
        curWeek = tgt.week

        # =======================================================
        # 指定された「施設」の予約状況ページを表示する。
        # ※日付は、この後のフェーズで 選択する。
        # =======================================================

        if curRoom != lstRoom:
            # 指定された 施設 の予約状況を確認
            url = "https://www.fureai-net.city.kawasaki.jp/user/view/user/homeIndex.html"
            self.driver.get(url)

            url = "https://www.fureai-net.city.kawasaki.jp/user/view/user/rsvNameSearch.html"
            self.driver.get(url)

            icd = dic.room_icd[curRoom]
            bname = curRoom.split('／')[0]
            iname = curRoom.split('／')[1]
            if "岡上" in bname:
                bname_key = bname + "分館"
            elif "サンピアン" in bname:
                bname_key = bname
            elif "教育文化" in bname:
                bname_key = bname
            else:
                bname_key = bname + "市民館"

            # vvv ちょっと待ってからスクリプト実行
            self.wait.until(EC.presence_of_element_located(
                (By.ID, "textKeyword")))
            self.driver.find_element_by_id('textKeyword').send_keys(bname_key)

            self.driver.execute_script("javascript:eventOnLoad()")
            # self.driver.find_element_by_id('doSearch').submit()
            self.driver.find_element_by_id('doSearch').click()

            self.driver.execute_script("javascript:eventOnLoad()")
            self.driver.find_element_by_id('doSelect').click()
            # self.driver.execute_script( "javascript:this.form.bcd.value = '1240';return true;")

            # チェックを全て解除
            self.driver.execute_script(
                "javascript:doCheck(false);return false;")
            # 特定の施設だけチェック

            chkboxs = self.driver.find_elements_by_name(
                'layoutChildBody:childForm:selectIcd')
            for chkbox in chkboxs:  # チェックボックスリストの中から該当する施設だけチェックする

                chkboxicd = chkbox.get_attribute("value")
                # print("icd:{}, chkboxicd:{}".format(icd,chkboxicd))

                if icd == chkboxicd:
                    print(bname, iname)
                    chkbox.click()

            # 表示の繁栄（リロード） ボタン押下
            self.driver.find_element_by_name(
                'layoutChildBody:childForm:doReload').click()

            # 施設名の取得

            print('■ 施設:{0}, 部屋:{1}'.format(bname, iname))
            # print('>> 期間： {0}/{1}～{2}/{3}'.format( date_from.month, date_from.day, date_to.month, date_to.day ))

            # room_str = '{0}/{1}'.format(bname, iname)
            rank = dic.chorus_ROOM[curRoom]

        lstRoom = curRoom

        # =======================================================
        # カレンダーから 指示された日付を クリック相当し
        # 指定された「施設」「日付」の予約状況ページを表示する
        # =======================================================

        # Webページ上の 対象施設の 日付の更新
        day_string = str(curYear) + "," + str(curMonth) + "," + str(curDay)
        script_str = "javascript:selectCalendarDate(" + \
            day_string + ");return false;"

        print('Script:' + script_str)

        # vvv ちょっと待ってからスクリプト実行
        # time.sleep(0.2)

        self.wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, 'calclick')))
        self.driver.execute_script(script_str)
        # print("# 日付：{0}/{1}({2}): 場所:{3}".
        #      format(month, day, curWeek, room_str), end="")

        time.sleep(0.2)  # 待ちを入れてみる

        # =======================================================
        # 表示されている ページから 予約状況 を 取得する
        # =======================================================
        #  class:'time-table1' は見出し行、'time-table2' は 予約状況
        rsvStat = ["", "", ""]

        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")  # html5lib

        # 予約テーブルの取得
        # 予約状況の取得
        #  class:'time-table1' は見出し行、'time-table2' は 予約状況
        table = soup.select_one('#isNotEmptyPager')
        if table is None:  # 予約なし
            return

        # 少なくとも１件以上の 施設情報がある（よい）
        tds = table.select('td.time-table2')
        for i in range(len(tds)):  # 3つの td で構成。0:午前, 1:午後, 2:夜
            td = tds[i]
            # sel_ele = td.select_one("#sel")
            # bcd_ele   = td.select_one("#bcd")
            # tzone_ele = td.select_one("#tzoneno")
            state_ele = td.select_one("#emptyStateIcon")

            # sel_name    = sel_ele.get("name")
            # sel_value = sel_ele.get("value")
            # bcd_name    = bcd_ele.get("name")
            # bcd_value   = bcd_ele.get("value")
            # tzone_name  = tzone_ele.get("name")
            # tzone_value = tzone_ele.get("value")
            state_alt = state_ele.get('alt')

            state = dic.state_tbl[state_alt]
            # tzone_str = dic.tzone_tbl[tzone_value]
            # rsvStat[i] = sel_value
            rsvStat[i] = state

        # リストに追加
        # room_stat.append([curYear, curMonth, curDay, curWeek, room_str, rsvStat])
        # room_dataat = namedtuple('room_dataat', ('year', 'month', 'day', 'week', 'room', 'am', 'pm', 'night'))

        # (
        #         'type',
        #         'username',
        #         'year', 'month', 'day', 'week',
        #         'start','end',
        #         'bname', 'iname',
        #         'state',
        #         'am', 'pm', 'night',
        #         'rank'
        # )
        room_data.append(
            room_datum(
                type="空き",
                username='---',  # username
                year=curYear,
                month=curMonth,
                day=curDay,
                week=curWeek,
                start='',
                end='',
                bname=bname,
                iname=iname,
                state='---',
                am=rsvStat[0],
                pm=rsvStat[1],
                night=rsvStat[2],
                rank=rank,
                Tmanabu='',
                Tsato='',
                Tniimi='',
                Ttamamura=''
            )
        )

        # print( room_data[-1] )

    return result_msg

# ---------------------------------
# 日付リスト に従い チェックする
# ※使用中
# ---------------------------------


def chk_free_room(self, lst):
    result_msg = ""

    lstRoom = ""
    for tgt in lst:

        # 施設指定
        curRoom = tgt.room
        curYear = tgt.year
        curMonth = tgt.month
        curDay = tgt.day
        curWeek = tgt.week

        if curRoom != lstRoom:
            # 指定された 施設 の予約状況を確認
            url = "https://www.fureai-net.city.kawasaki.jp/user/view/user/homeIndex.html"
            self.driver.get(url)

            url = "https://www.fureai-net.city.kawasaki.jp/user/view/user/rsvNameSearch.html"
            self.driver.get(url)

            icd = dic.room_icd[curRoom]
            bname = curRoom.split('／')[0]
            iname = curRoom.split('／')[1]
            if "岡上" in bname:
                bname_key = bname + "分館"
            elif "サンピアン" in bname:
                bname_key = bname
            elif "教育文化" in bname:
                bname_key = bname
            else:
                bname_key = bname + "市民館"

            # vvv ちょっと待ってからスクリプト実行
            self.wait.until(EC.presence_of_element_located(
                (By.ID, "textKeyword")))
            self.driver.find_element_by_id('textKeyword').send_keys(bname_key)

            self.driver.execute_script("javascript:eventOnLoad()")
            # self.driver.find_element_by_id('doSearch').submit()
            self.driver.find_element_by_id('doSearch').click()

            self.driver.execute_script("javascript:eventOnLoad()")
            self.driver.find_element_by_id('doSelect').click()
            # self.driver.execute_script( "javascript:this.form.bcd.value = '1240';return true;")

            # チェックを全て解除
            self.driver.execute_script(
                "javascript:doCheck(false);return false;")
            # 特定の施設だけチェック

            chkboxs = self.driver.find_elements_by_name(
                'layoutChildBody:childForm:selectIcd')
            for chkbox in chkboxs:  # チェックボックスリストの中から該当する施設だけチェックする

                chkboxicd = chkbox.get_attribute("value")
                # print("icd:{}, chkboxicd:{}".format(icd,chkboxicd))

                if icd == chkboxicd:
                    print(bname, iname)
                    chkbox.click()

            # 表示の繁栄（リロード） ボタン押下
            self.driver.find_element_by_name(
                'layoutChildBody:childForm:doReload').click()

            # 施設名の取得

            print('■ 施設:{0}, 部屋:{1}'.format(bname, iname))
            # print('>> 期間： {0}/{1}～{2}/{3}'.format( date_from.month, date_from.day, date_to.month, date_to.day ))

            # room_str = '{0}/{1}'.format(bname, iname)
            rank = dic.chorus_ROOM[curRoom]

        lstRoom = curRoom

        # === 日付ループ ===

        # Webページ上の 対象施設の 日付の更新
        day_string = str(curYear) + "," + str(curMonth) + "," + str(curDay)
        script_str = "javascript:selectCalendarDate(" + \
            day_string + ");return false;"

        print('Script:' + script_str)

        # vvv ちょっと待ってからスクリプト実行
        # time.sleep(0.2)

        self.wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, 'calclick')))
        self.driver.execute_script(script_str)
        # print("# 日付：{0}/{1}({2}): 場所:{3}".
        #      format(month, day, curWeek, room_str), end="")

        time.sleep(0.2)  # 待ちを入れてみる

        # 予約状況の取得
        #  class:'time-table1' は見出し行、'time-table2' は 予約状況
        rsvStat = ["", "", ""]
        tds = self.driver.find_elements_by_class_name('time-table2')
        for i in range(len(tds)):  # 3つの td で構成。0:午前, 1:午後, 2:夜
            td = tds[i]
            # sel_ele = td.find_element_by_id("sel")
            # bcd_ele   = td.find_element_by_id("bcd")
            # tzone_ele = td.find_element_by_id("tzoneno")
            state_ele = td.find_element_by_tag_name("img")

            # sel_name    = sel_ele.get_attribute("name")
            # sel_value = sel_ele.get_attribute("value")
            # bcd_name    = bcd_ele.get_attribute("name")
            # bcd_value   = bcd_ele.get_attribute("value")
            # tzone_name  = tzone_ele.get_attribute("name")
            # tzone_value = tzone_ele.get_attribute("value")
            state_alt = state_ele.get_attribute("alt")

            state = dic.state_tbl[state_alt]
            # tzone_str = dic.tzone_tbl[tzone_value]
            # rsvStat[i] = sel_value
            rsvStat[i] = state

        # リストに追加
        # room_stat.append([curYear, curMonth, curDay, curWeek, room_str, rsvStat])
        # room_dataat = namedtuple('room_dataat', ('year', 'month', 'day', 'week', 'room', 'am', 'pm', 'night'))

        # (
        #         'type',
        #         'username',
        #         'year', 'month', 'day', 'week',
        #         'start','end',
        #         'bname', 'iname',
        #         'state',
        #         'am', 'pm', 'night',
        #         'rank'
        # )
        room_data.append(
            room_datum(
                type="空き",
                username='---',  # username
                year=curYear,
                month=curMonth,
                day=curDay,
                week=curWeek,
                start='',
                end='',
                bname=bname,
                iname=iname,
                state='---',
                am=rsvStat[0],
                pm=rsvStat[1],
                night=rsvStat[2],
                rank=rank,
                Tmanabu='',
                Tsato='',
                Tniimi='',
                Ttamamura=''
            )
        )

        # print( room_data[-1] )

    return result_msg
