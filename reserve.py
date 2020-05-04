# 日付操作系 ライブラリ
import time

# WebDriver系
# from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# import chromedriver_binary  # Adds chromedriver binary to path

# import subs.datesub as datesub

# data, 辞書 インポート
# import data.data as data
import data.data as dic
# from data.data import room_data, room_datum


def reserve_room(self, rsv_list):
    result_msg = ""

    for login_name in ['歌の会']:

        # ログイン
        result_msg += self._login(login_name)

        # ログインできなかったら コンティニュー
        if self.login_state is False:
            continue

        # 抽選申し込み状況・結果確認
        result_msg += _reserve_room(self, rsv_list)

        # 最後にログオフ
        result_msg += self._logoff()

    return result_msg

# 日付リスト で指定された 予約を実行


def _reserve_room(self, rsv_list):

    result_msg = ""
    for rsv_data in rsv_list:

        # ログインしていることが前提

        # 処理対象情報表示
        print('予約情報：{}/{}/{} {} {}\n'.format(rsv_data.year, rsv_data.month, rsv_data.day, rsv_data.zone, rsv_data.room))

        # マイページを開く
        script_str = "javascript:return doMenuBtn('MYPAGE');"
        # vvv ボタンが押せるまで待って スクリプト実行
        self.wait.until(EC.element_to_be_clickable((By.ID, 'goBtn')))
        self.driver.execute_script(script_str)

        # 指定の施設を開く
        # chorus_room = rsv_data.bname+"／"+rsv_data.iname
        chorus_room = rsv_data.room
        icd = dic.room_icd[chorus_room]
        bcd = dic.room_bcd[chorus_room]

        url = "https://www.fureai-net.city.kawasaki.jp/user/view/user/rsvEmptyState.html?"
        url = url + "bcd=" + bcd + "&icd=" + icd
        self.driver.get(url)

        # Webページ上の 対象施設の 日付の更新
        rsvYear = rsv_data.year
        rsvMonth = rsv_data.month
        rsvDay = rsv_data.day

        day_string = str(rsvYear) + "," + str(rsvMonth) + "," + str(rsvDay)
        script_str = "javascript:selectCalendarDate(" + \
            day_string + ");return false;"

        print('Script:' + script_str)

        # vvv ちょっと待ってからスクリプト実行
        # time.sleep(0.2)

        self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'calclick')))
        self.driver.execute_script(script_str)

        # ========================================
        # Step 1: 予約申込画面
        #   空き をクリックし
        #   [予約カートに追加]を押して
        #   [予約カートの確認]を押す→予約カートの確認画面に遷移
        # ========================================

        # === ここまでで 施設・日時が 表示された ===
        state_alt = ['', '', '']
        css_selector = 'img#emptyStateIcon'
        EmptyStates = self.driver.find_elements_by_css_selector(css_selector)
        for i, stat in enumerate(EmptyStates):
            state_alt[i] = stat.get_attribute('id')
            state_alt[i] = stat.get_attribute('src')
            state_alt[i] = stat.get_attribute('style')
            state_alt[i] = stat.get_attribute('alt')
            print(i, state_alt)

        if rsv_data.zone == '夜間':
            script_str = 'return doSelectBtn(this, 0, 0, 2);'
            tgt_zone = 2
        if rsv_data.zone == '午後':
            script_str = 'return doSelectBtn(selenium, 0, 0, 1);'
            tgt_zone = 1
        if rsv_data.zone == '午前':
            script_str = 'return doSelectBtn(this, 0, 0, 0);'
            tgt_zone = 0

        # ターゲットのゾーンが 空きじゃない時は 何もせず戻る
        if state_alt[tgt_zone] == "空き":  # 予約できる
            print('空き→予約可能')
        else:  # 予約できない
            print('空きではない： state:', state_alt[tgt_zone])
            continue

        # 該当する 午前・午後・夜間 のボタンをクリックし カート追加済みにする

        # ボタンの状態を確認

        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        if EC.element_to_be_clickable(EmptyStates[tgt_zone]):
            print('clickableらしい')
            EmptyStates[tgt_zone].click()

        # self.driver.execute_script(script_str)

        # 予約カートに追加 ボタンを押す
        css_selector = 'input#doAddCart'
        doAddCart = self.driver.find_element_by_css_selector(css_selector)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        if EC.element_to_be_clickable(doAddCart):
            print('clickableらしい')
            doAddCart.click()

        # script_str = "javascript: this.form.itemindex.value = '0'; return true;"
        # script_str = "javascript: selenium.form.itemindex.value = '0'; return true;"
        # self.driver.execute_script(script_str)

        # vvv ちょっと待ってからスクリプト実行
        time.sleep(0.5)

        # 予約カートの内容を確認ボタンを押す
        css_selector = 'input#jumpRsvCartList'
        jumpRsvCartList = self.driver.find_element_by_css_selector(css_selector)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        if EC.element_to_be_clickable(jumpRsvCartList):
            print('clickableらしい')
            jumpRsvCartList.click()

        # script_str = "return confirmSelCart(-1);"
        # self.wait.until(EC.element_to_be_clickable((By.ID, 'jumpRsvCartList')))
        # self.driver.execute_script(script_str)

        # ========================================
        # Step 2: 予約カートの確認・予約申し込み画面
        #   [予約確定の手続きへ]を押して
        #   →予約カートの確認画面に遷移
        # ========================================

        # vvv ちょっと待ってからスクリプト実行
        time.sleep(0.5)

        # 予約カートの内容を確認ボタンを押す
        css_selector = 'input#doCartDetails'
        doCartDetails = self.driver.find_element_by_css_selector(css_selector)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        if EC.element_to_be_clickable(doCartDetails):
            print('clickableらしい')
            doCartDetails.click()

        # ========================================
        # Step 3: 予約詳細情報入力画面
        #   利用目的、目的の詳細、利用人数を入力し
        #   [予約内容を確認する]を押して
        #   →予約内容確認画面に遷移
        # ========================================

        # vvv ちょっと待ってからスクリプト実行
        time.sleep(0.5)

        # 詳細情報準備
        purpose = dic.room_purpose[chorus_room]
        purposeDetails = "合唱練習"
        useCnt = 20

        # 詳細情報記入
        self.driver.find_element_by_id('purpose').send_keys(purpose)
        self.driver.find_element_by_id('purposeDetails').send_keys(purposeDetails)

        self.driver.find_element_by_id('useCnt').send_keys(Keys.CONTROL, "a")
        self.driver.find_element_by_id('useCnt').send_keys(Keys.DELETE)
        self.driver.find_element_by_id('useCnt').send_keys(str(useCnt))

        # 確認ボタンクリック
        self.driver.find_element_by_id('doConfirm').click()

        # 予約カートの内容を確認ボタンを押す
        css_selector = 'input#doOnceLockFix'
        doOnceLockFix = self.driver.find_element_by_css_selector(css_selector)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        if EC.element_to_be_clickable(doOnceLockFix):
            print('clickableらしい')
            doOnceLockFix.click()

    return result_msg
