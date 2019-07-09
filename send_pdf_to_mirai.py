#!/usr/bin/python3
# coding:utf-8
# 参考: https://arakan-pgm-ai.hatenablog.com/entry/2018/01/07/080000
# 参考: https://www.haya-programming.com/entry/2018/03/22/175925

"""
pdfを読み取ってみらい翻訳に投げるスクリプト
"""
import sys
import os
import re
# from time import time
from time import sleep
from io import StringIO
# from getpass import getpass  # パスワード入力用
from selenium import webdriver
# from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from pysnooper import snoop

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage


# ブラウザを指定(Firefox,Chrome,Edge)
BROWSER_NAME = 'Chrome'
# 実行ファイルの絶対パスを取得
ABS_DIRNAME = os.path.dirname(os.path.abspath(__file__))

# ここからコピペ


def gettext(pdfname):
    """
    PDFファイルを読み取って文字列を返す関数
    """
    # PDFファイル名が未指定の場合は、空文字列を返して終了
    if pdfname == '':
        return ''

    # 処理するPDFファイルを開く/開けなければ
    try:
        fp = open(pdfname, 'rb')
    except:
        return ''

    # リソースマネージャインスタンス
    rsrcmgr = PDFResourceManager()
    # 出力先インスタンス
    outfp = StringIO()
    # パラメータインスタンス
    laparams = LAParams()
    # 縦書き文字を横並びで出力する
    laparams.detect_vertical = True
    # デバイスの初期化
    device = TextConverter(rsrcmgr, outfp, codec='utf-8', laparams=laparams)
    # テキスト抽出インタプリタインスタンス
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # 対象ページを読み、テキスト抽出する。（maxpages：0は全ページ）
    for page in PDFPage.get_pages(fp, pagenos=None, maxpages=0, password=None, caching=True, check_extractable=True):
        interpreter.process_page(page)
    # 取得したテキストをすべて読みだす
    ret = outfp.getvalue()
    # 後始末をしておく
    fp.close()
    device.close()
    outfp.close()
    # 空白と改行をとりさり一塊のテキストとして返す
    return re.sub(r"\s|　", '', ret)

# ------------ここまでコピペ-------------------------


def select_driver(browser):
    """
    webドライバーを指定する関数
    """
    # Windowsで実行された場合
    if os.name == 'nt':
        print('{} on Windows'.format(browser))
        try:
            if browser == 'Firefox':
                driver = webdriver.Firefox(
                    executable_path=R'C:\Programing\Drivers\webdrivers\geckodriver.exe')
            elif browser == 'Chrome':
                driver = webdriver.Chrome(
                    executable_path=R'C:\Programing\Drivers\webdrivers\chromedriver.exe')
            elif browser == 'Edge':
                driver = webdriver.Edge(
                    executable_path=R'C:\Programing\Drivers\webdrivers\webdriver.exe')
            else:
                input('Firefox, Chrome, Edge のみ対応しています。')
                sys.exit()
        except FileNotFoundError:
            print('Error')
            print('ウェブドライバーが見つかりませんでした。')
            print('ソースコード中のPATHを設定し直してください。')
            input('Press enter to Exit.\n')
            sys.exit()
        return driver

    # WSLで実行された場合
    if os.name == 'posix':
        print('{} on WSL'.format(browser))
        try:
            if browser == 'Firefox':
                driver = webdriver.Firefox(
                    executable_path='/mnt/c/programing/drivers/webdrivers/geckodriver.exe')
            elif browser == 'Chrome':
                driver = webdriver.Chrome(
                    executable_path='/mnt/c/programing/drivers/webdrivers/chromedriver.exe')
            elif browser == 'Edge':
                driver = webdriver.Edge(
                    executable_path='/mnt/c/programing/drivers/webdrivers/webdriver.exe')
            else:
                input('Firefox, Chrome, Edge のみ対応しています。')
                sys.exit()
        except FileNotFoundError:
            print('Error')
            print('ウェブドライバーが見つかりませんでした。')
            print('ソースコード中のPATHを設定し直してください。')
            input('Press enter to Exit.\n')
            sys.exit()
        return driver

    # Mac,Linuxなどで実行された場合
    print('Error')
    print('os.name:', os.name)
    print('WindowsとWSLしかOS対応していません。')
    print('ソースコード中のウェブドライバーのPATHを適切に設定すれば使えます。')
    input('Press enter to exit.\n')
    sys.exit()


def trim_txt(txt):
    """
    文章を5文ごとに分けてリストで返す
    """
    # テキストをピリオドで区切ってリストにする
    # ピリオドが消えるから元に戻す
    l_1 = []
    for sentence in re.split('.', txt):
        if sentence != '.':
            l_1.append(sentence)
        elif sentence == '':
            pass
        else:
            l_1[-1] += sentence

    # 5文ごとにまとめる
    l_2 = []
    n = len(l_1) // 5
    for i in range(n):
        l_2.append(l_1[i * 5: (i + 1) * 5])
    l_2.append(l_1[(i + 1) * 5:])

    # 5文ごとのリストを返す
    return l_2


def use_miraitranslate(d, l):
    """
    文字列をみらい翻訳に送りつけて、翻訳結果を文字列で返す関数
    d: webdriver, txt: 翻訳したい文章
    """
    wait = WebDriverWait(d, 10)
    # サイトを開く
    d.get('https://miraitranslate.com/trial/')
    wait.until(EC.presence_of_all_elements_located)
    d.find_element_by_class_name('sourceLanguageDiv').click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/span/span/span[2]/ul/li[2]')))
    d.find_element_by_xpath('/html/body/span/span/span[2]/ul/li[2]').click()
    d.find_element_by_id('translateSourceInput').click()

    translated = ''
    print(l)
    for en in l:
        sleep(5)
        d.find_element_by_id('translateSourceInput').send_keys(en)
        sleep(5)
        d.find_element_by_id('translateButtonTextTranslation').click()
        sleep(5)
        ja = d.find_element_by_id('translate-text').getAttribute('value')
        translated += ja
    return translated


def main():
    pdfname = ABS_DIRNAME + '/' + input('PDFファイル名を入力してください。\n>>> ')

    print('PDFを読み取ります。')
    txt = gettext(pdfname)
    print(txt)
    print('PDFを読み取りました。')

    print('みらい翻訳で翻訳します。')
    l = trim_txt(txt)
    translated = use_miraitranslate(select_driver(BROWSER_NAME), l)
    print('みらい翻訳が完了しました。')

    print('ファイル出力を開始します。')
    path = ABS_DIRNAME + '/mirai_output.txt'
    with open(path, mode='w') as f:
        f.write(translated)
    print('ファイル出力が完了しました。')


if __name__ == '__main__':
    main()
    input('Press enter to quit.')
