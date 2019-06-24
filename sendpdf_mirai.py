#!/usr/bin/python3
# coding:utf-8
# 参考: https://arakan-pgm-ai.hatenablog.com/entry/2018/01/07/080000

"""
pdfを読み取ってみらい翻訳に投げるスクリプト
"""
import sys
import os
from time import time
from time import sleep
from getpass import getpass  # パスワード入力用
from selenium import webdriver
from selenium.webdriver.common.alert import Alert
# from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# import termcolor
# from pysnooper import snoop

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import re


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
    if (pdfname == ''):
        return ''
    else:
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


def use_miraitranslate(driver, long_txt):
    """
    文字列をみらい翻訳に送りつけて、翻訳結果を文字列で返す関数
    """
    # テキストを5文ごとに区切ってリストにする
    l_input = 
    #

    # サイトを開く
    driver.get('https://miraitranslate.com/trial/')
