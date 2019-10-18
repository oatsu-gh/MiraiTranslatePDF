#!/usr/bin/python3
# coding:utf-8
# 参考: https://arakan-pgm-ai.hatenablog.com/entry/2018/01/07/080000
# 参考: https://www.haya-programming.com/entry/2018/03/22/175925

"""
pdfを読み取ってみらい翻訳に投げるスクリプト
"""
import os
import re
import subprocess
import sys
from io import StringIO
from multiprocessing import Pool, cpu_count
from pprint import pprint
from time import sleep, time

# import chromedriver_binary
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
# from getpass import getpass  # パスワード入力用
# import codecs
from tqdm import tqdm

# from pysnooper import snoop

# ブラウザを指定(Firefox,Chrome,Edge)
BROWSER_NAME = 'Firefox'
# 実行ファイルの絶対パスを取得
ABS_DIRNAME = os.path.dirname(os.path.abspath(__file__))
# テストモード（有効にすると標準出力が増える）
TEST_MODE = False
# OCRモード（古い文書を使うときに有効にする）
OCR_MODE = False
# スレッド数（ブラウザの起動個数）
if cpu_count() == 4:
    THREAD_NUM = 3
else:
    THREAD_NUM = cpu_count() // 2


def gettext(filepath):
    """
    PDFファイルを読み取って文字列を返す関数
    ほぼコピペ→https://arakan-pgm-ai.hatenablog.com/entry/2018/01/07/080000
    """
    # PDFファイル名が未指定の場合は、空文字列を返して終了
    if filepath == '':
        return ''

    # 処理するPDFファイルを開く/開けなければ
    try:
        fp = open(filepath, 'rb')
    except FileNotFoundError as e:
        print(e)
        print('Press Enter to exit.')
        sys.exit()

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
    path = ABS_DIRNAME + '/mirai_output2(gettext).txt'
    with open(path, mode='wb') as f:
        f.write(ret.encode('cp932', 'ignore'))
    return ret


def split_txt(txt):
    """
    文章を区切ってリストで返す
    txt:文章の文字列
    """
    # テキストを改行で区切ってリストで返す
    l = list(re.split('.\n|. \n|.  \n', txt))
    if TEST_MODE:
        print('l:')
        pprint(l)

    # 空文字列を除去
    # l = filter(lambda str: str != '', l)
    l = filter(lambda str: str != '\x0c', l)
    # l = filter(lambda str: str != '\xa9', l)
    # l = filter(lambda str: str != '\xf1', l)
    l = list(l)

    s2 = ''
    l_2 = []

    n = len(l)
    for i in range(n):
        s1 = l[i].replace('-\n', '').replace('- \n', '')
        s1 = s1.replace('\n', ' ') + '. '
        len_s1 = len(s1)
        # print('len_s1 =', len_s1)
        # 文章があわせて1800文字未満の場合は、いまの段落を文章に追加して長くする。
        if len(s2) + len_s1 < 2000:
            s2 += s1
            s2 = s2.replace('  ', '\n\n').replace('.[', '.\n[').replace('. [', '.\n[')

        # 1800文字以上の場合は、ここまでの段落をリストに加えて、今の文章と区切る。
        elif len_s1 < 2000:
            l_2.append(s2)
            s2 = s1.replace('  ', '\n\n').replace('.[', '.\n[').replace('. [', '.\n[')

        # とくに、いまの段落単独で1800文字を超える場合は1000~1800文字付近の文末で分割する。
        else:
            l_2.append(s2)
            s1 = s1.replace('  ', '\n\n').replace('.[', '.\n[').replace('. [', '.\n[')
            x = s1.find('. ', 1500, 2000) + 2
            l_2.append(s1[:x])
            s2 = s1[x:]

        # 最後の文章のとき
        if i == n - 1:
            l_2.append(s2)
    return l_2


def split_txt_ocrmode(txt):
    """
    文章を区切ってリストで返す
    txt:文章の文字列
    """
    # テキストを改行で区切ってリストで返す
    l = list(re.split('.\n|. \n|.  \n', txt))
    if TEST_MODE:
        print('l:')
        pprint(l)

    # 空文字列を除去
    # l = filter(lambda str: str != '', l)
    l = filter(lambda str: str != '\x0c', l)
    # l = filter(lambda str: str != '\xa9', l)
    # l = filter(lambda str: str != '\xf1', l)
    l = list(l)

    s2 = ''
    l_2 = []

    n = len(l)
    for i in range(n):
        s1 = l[i].replace('-\n', '').replace('- \n', '').replace('  ', ' ')
        s1 = s1.replace('\n', ' ') + '. '
        len_s1 = len(s1)
        # print('len_s1 =', len_s1)
        # 文章があわせて2000文字未満の場合は、いまの段落を文章に追加して長くする。
        if len(s2) + len_s1 < 2000:
            s2 += s1
            # s2 = s2.replace('  ', '\n\n')

        # 2000文字以上の場合は、ここまでの段落をリストに加えて、今の文章と区切る。
        elif len_s1 < 2000:
            l_2.append(s2)
            s2 = s1
            # s2 = s1.replace('  ', '\n\n')

        # とくに、いまの段落単独で2000文字を超える場合は1000~2000文字付近の文末で分割する。
        else:
            l_2.append(s2)
            # s1 = s1.replace('  ', '\n\n')
            x = s1.find('. ', 1000, ) + 2
            l_2.append(s1[:x])
            s2 = s1[x:]

        # 最後の文章のとき
        if i == n - 1:
            l_2.append(s2)

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
            elif browser == 'HL_Chrome':
                options = webdriver.ChromeOptions()
                options.add_argument('--headless')
                driver = webdriver.Chrome(
                    executable_path=R'C:\Programing\Drivers\webdrivers\chromedriver.exe',
                    options=options)
            else:
                input('Firefox, Chrome のみ対応しています。')
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
            elif browser == 'HL_Chrome':
                options = webdriver.ChromeOptions()
                options.add_argument('--headless')
                driver = webdriver.Chrome(
                    executable_path='/mnt/c/programing/drivers/webdrivers/chromedriver.exe',
                    options=options)
            else:
                input('Firefox, Chrome のみ対応しています。')
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
def use_miraitranslate(l):
    """
    文字列をみらい翻訳に送りつけて、翻訳結果を文字列で返す関数
    l: 翻訳したい文章のリスト
    """
    # ブラウザパスの指定
    d = select_driver(BROWSER_NAME)
    # サイトを開く
    d.get('https://miraitranslate.com/trial/')
    sleep(3)

    wait = WebDriverWait(d, 30)
    wait.until(EC.presence_of_all_elements_located)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'sourceLanguageDiv')))

    # 原文言語を日本語に設定
    d.find_element_by_class_name('sourceLanguageDiv').click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/span/span/span[2]/ul/li[2]')))
    d.find_element_by_xpath('/html/body/span/span/span[2]/ul/li[2]').click()

    # 原文入力欄を記憶
    # txt_in = d.find_element_by_id('translateSourceInput')

    # 翻訳作業
    i = 0
    d_t = 0.0
    answer = ''
    for v in tqdm(l):
        if v == '':
            continue

        # 原文を入力
        d.find_element_by_id('translateSourceInput').send_keys(v)
        sleep(1)
        # 翻訳ボタンをクリック
        wait.until(EC.element_to_be_clickable((By.ID, 'translateButtonTextTranslation')))
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'loader')))
        t_start = time()
        d.find_element_by_id('translateButtonTextTranslation').click()
        # ロード画面になるまで時間をおく
        sleep(1)
        # 翻訳完了まで待つ
        wait.until(EC.element_to_be_clickable((By.ID, 'translate-text')))
        sleep(0.5)
        # 翻訳結果を取得
        translated = d.find_element_by_id('translate-text').text + '\n'
        answer += translated
        # 原文を消去
        d.find_element_by_id('translateSourceInput').clear()

        d_t += time() - t_start
        print('\ni={}  len={}  {:.3f} s'.format(i, len(v), d_t))

        # 60秒に10回までの制限対策
        if i == 9 and d_t <= 60:
            print('waiting...')
            sleep(61 - d_t)
            i = 0
            d_t = 0.0
        elif d_t > 60:
            i = 0
        i += 1

    # ブラウザを閉じる
    d.quit()

    return answer


def divide_list(l, n):
    """
    リスト l を n 分割する関数
    """
    idx = 0
    l_div = []
    # リスト長さをnで割った商とあまり
    num, amari = divmod(len(l), n)
    for i in range(n):
        if i >= n - amari:
            l_div.append(l[idx: idx + num + 1])
            idx += num + 1
        else:
            l_div.append(l[idx: idx + num])
            idx += num

    return l_div


def main():
    """
    1. PDFファイル名を指定
    2. PDFファイルからテキストを読み取る
    3. テキストを段落で区切る
    4. 適当な長さになるように段落を連結する（2000字以内制限のため）
    4. みらい翻訳に送って翻訳する
    5. 翻訳結果をTXTファイルに保存する
    """
    print('BROWSER  :', BROWSER_NAME)
    print('OCR_MODE :', OCR_MODE)
    print('TEST_MODE:', TEST_MODE)

    # 英語論文のpathをコマンドライン引数で指定
    try:
        filepath = sys.argv[1]
    # コマンドライン引数で指定されていない場合
    except IndexError:
        filepath = ABS_DIRNAME + '/' + input('PDFファイル名を入力してください。\n>>> ')

    print('PDFを読み取ります。')
    txt = gettext(filepath)
    if TEST_MODE:
        print('----------pdf----------')
        pprint(txt)
        print('----------pdf----------\n')
    print('PDFを読み取りました。')

    print('文章を分割します。')
    if OCR_MODE:
        l = split_txt_ocrmode(txt)
    else:
        l = split_txt(txt)
    if TEST_MODE:
        print('l:')
        print(l)
    print('文章を{}分割しました。'.format(len(l)))

    try:
        print('みらい翻訳で翻訳します。')
        # コア数を数える
        n = THREAD_NUM
        if len(l) < 10:
            translated = use_miraitranslate(l)
        else:
            print('{}スレッドで処理します。'.format(n))
            l_div = divide_list(l, n)
            # print('\nl1 =', l1)
            # print('\nl2 =', l2)
            pool = Pool(n)
            translated_multi = pool.map(use_miraitranslate, [v for v in l_div])
            translated = ''.join(translated_multi)

        print('みらい翻訳が完了しました。')

        print('ファイル出力を開始します。')
        filepath = filepath + '_和訳.txt'
        with open(filepath, mode='wb') as f:
            f.write(translated.encode('cp932', 'ignore'))
        print('ファイル出力が完了しました。')

    except AttributeError as e:
        print('AttributeError:', e)
        print('失敗しました。')

    except exceptions.ElementClickInterceptedException as e:
        print('ElementClickIntercepted:', e)
        print('失敗しました。')
    except exceptions.TimeoutException as e:
        print('Timeout:', e)
        print('失敗しました。')

    # Windows, WSLで実行された場合に限り、出力結果をメモ帳で開く。
    if os.name in ('nt', 'posix'):
        print('メモ帳で開きます。')
        filepath = (filepath).replace('/mnt/c/', 'C:/')
        subprocess.Popen([r'notepad.exe', filepath])
    input('Press enter to quit.')

if __name__ == '__main__':
    main()
