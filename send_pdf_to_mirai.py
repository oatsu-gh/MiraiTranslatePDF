#!/usr/bin/python3
# coding:utf-8
# 参考: https://arakan-pgm-ai.hatenablog.com/entry/2018/01/07/080000
# 参考: https://www.haya-programming.com/entry/2018/03/22/175925

"""
pdfを読み取ってみらい翻訳に投げるスクリプト
"""
import os
import subprocess
# import re
import sys
from io import StringIO
# from getpass import getpass  # パスワード入力用
from pprint import pprint
# from time import time
from time import sleep

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
# from pysnooper import snoop
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm

# ブラウザを指定(Firefox,Chrome,Edge)
BROWSER_NAME = 'Firefox'
# 実行ファイルの絶対パスを取得
ABS_DIRNAME = os.path.dirname(os.path.abspath(__file__))

# テストモード（有効にすると標準出力が増える）
TEST_MODE = False


def gettext(pdfname):
    """
    PDFファイルを読み取って文字列を返す関数
    ほぼコピペ→https://arakan-pgm-ai.hatenablog.com/entry/2018/01/07/080000
    """
    # PDFファイル名が未指定の場合は、空文字列を返して終了
    if pdfname == '':
        return ''

    # 処理するPDFファイルを開く/開けなければ
    try:
        fp = open(pdfname, 'rb')
    except FileNotFoundError as e:
        print(e)
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
    pages = PDFPage.get_pages(fp, pagenos=None, maxpages=0, caching=True, check_extractable=True)
    for page in pages:
        interpreter.process_page(page)
    # 取得したテキストをすべて読みだす
    ret = outfp.getvalue()
    # 後始末をしておく
    fp.close()
    device.close()
    outfp.close()
    # 空白と改行をとりさり一塊のテキストとして返す
    # return re.sub(r"\s|　", '', ret)
    return ret

# ------------ここまでコピペ-------------------------


def split_txt(txt):
    """
    文章を区切ってリストで返す
    txt:文章の文字列
    """
    # 文を区切る長さ
    # n = 5

    # テキストをピリオドで区切ってリストにする
    # ピリオドが消えるから元に戻す
    # l_1 = list(txt.split('.'))
    # for i in range(len(l_1)):
    #     if l_1[i] not in ('\n', '\n\n', '\n\n\x0c'):
    #         l_1[i] += '.'

    # 5文ごとにまとめる
    # l_2 = []
    # m = len(l_1) // n
    # for i in range(m + 1):
    #     l_2.append(l_1[i * 5: (i + 1) * 5])
    #     l_2.append(l_1[(i + 1) * 5:])

    # 5文ごとのリストを返す
    # return l_2

    # テキストを改行で区切ってリストで返す
    l_1 = list(txt.split('\n'))
    tmp = ''
    l_2 = []
    for v in l_1:
        if len(tmp) < 1000:
            tmp += v
        else:
            l_2.append(tmp)
            tmp = ''
    return l_2



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


# @snoop()
def use_miraitranslate(d, l):
    """
    文字列をみらい翻訳に送りつけて、翻訳結果を文字列で返す関数
    d: webdriver, txt: 翻訳したい文章
    """
    # 空文字列を除去
    l = filter(lambda str: str != '', l)
    l = filter(lambda str: str != '\x0c', l)

    # サイトを開く
    d.get('https://miraitranslate.com/trial/')

    wait = WebDriverWait(d, 10)
    wait.until(EC.presence_of_all_elements_located)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'sourceLanguageDiv')))

    # 原文言語を日本語に設定
    d.find_element_by_class_name('sourceLanguageDiv').click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/span/span/span[2]/ul/li[2]')))
    d.find_element_by_xpath('/html/body/span/span/span[2]/ul/li[2]').click()

    # 原文入力欄を記憶
    # txt_in = d.find_element_by_id('translateSourceInput')

    # 翻訳作業
    answer = ''
    for v in tqdm(l):
        # 原文を入力
        d.find_element_by_id('translateSourceInput').send_keys(v)
        sleep(2)
        # 翻訳ボタンをクリック
        wait.until(EC.element_to_be_clickable((By.ID, 'translateButtonTextTranslation')))
        d.find_element_by_id('translateButtonTextTranslation').click()
        sleep(4)
        wait.until(EC.element_to_be_clickable((By.ID, 'translate-text')))
        # 翻訳結果を取得
        translated = d.find_element_by_id('translate-text').text + '\n'
        answer += translated
        # 原文を消去
        d.find_element_by_id('translateSourceInput').clear()

    return answer


def main():
    """
    1. PDFファイル名を指定
    2. PDFファイルからテキストを読み取る
    3. テキストを改行で区切る
    4. みらい翻訳に送って翻訳する
    5. 翻訳結果をTXTファイルに保存する
    """
    pdfname = ABS_DIRNAME + '/' + input('PDFファイル名を入力してください。\n>>> ')
    # pdfname = ABS_DIRNAME + '/input.pdf'

    print('PDFを読み取ります。')
    txt = gettext(pdfname)
    if TEST_MODE:
        print('----------pdf----------')
        print(txt)
        print('----------pdf----------\n')
    print('PDFを読み取りました。')

    print('文章を分割します。')
    l = split_txt(txt)
    if TEST_MODE:
        print('l:')
        pprint(l)
    print('文章を分割しました。')

    try:
        print('ブラウザを起動します。')
        d = select_driver(BROWSER_NAME)
        print('みらい翻訳で翻訳します。')
        translated = use_miraitranslate(d, l)
        print('みらい翻訳が完了しました。')
        d.close()
        print('ブラウザを終了しました。')

        print('ファイル出力を開始します。')
        path = ABS_DIRNAME + '/mirai_output.txt'
        with open(path, mode='w') as f:
            f.write(translated)
        print('ファイル出力が完了しました。')

    except AttributeError as e:
        print(e)
        d.close()
        print('失敗しました。')

    except exceptions.ElementClickInterceptedException as e:
        print(e)
        d.close()
        print('失敗しました。')
    except exceptions.TimeoutException as e:
        print(e)
        d.close()
        print('失敗しました。')


if __name__ == '__main__':
    main()

    # Windows, WSLで実行された場合に限り、出力結果をメモ帳で開く。
    if os.name in ('nt', 'posix'):
        print('メモ帳で開きます。')
        file_path = (ABS_DIRNAME + r'/mirai_output.txt').replace('/mnt/c/', 'C:/')
        subprocess.Popen([r'notepad.exe', file_path])
        print('終了します。')
        sys.exit()
    input('Press enter to quit.')
