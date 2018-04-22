import requests
from bs4 import BeautifulSoup
import inspect
from pdb import set_trace as BP
import os
import time
import yaml
import smtplib
from pprint import pprint

path_base = os.path.dirname(os.path.abspath(__file__)) + '/'
glo_credGmailAutotrading = 'credGmailAutotrading'
glo_alreadyMatched = []
seconds_to_sleep = 300

def sendEmail(sbj, body):
    print ('\nSTART', inspect.stack()[0][3])
    try:
        msg = 'Subject: {}\n\n{}'.format(sbj, body)
        smtp = smtplib.SMTP('smtp.gmail.com:587')
        smtp.starttls()
        credGmailAutotrading = getCredentials(glo_credGmailAutotrading)
        smtp.login(credGmailAutotrading.get('username'), credGmailAutotrading.get('pwd'))
        smtp.sendmail(credGmailAutotrading.get('username'), credGmailAutotrading.get('username'), msg) # 1 from, 2 to
    except Exception as e:
        print ('ERROR in function' ,inspect.stack()[0][3], ':', str(e))
    else:
        print('END', inspect.stack()[0][3], '\n')

def getCredentials(domain):
    try:
        if domain == glo_credGmailAutotrading:
            conf = yaml.load(open(path_base + 'credentials.yml'))
            username = conf['gmail_autotrade']['username']
            pwd = conf['gmail_autotrade']['password']
            return {'username': username, 'pwd': pwd}
    except Exception as e:
        print ('ERROR in function' ,inspect.stack()[0][3], ':', str(e))

def isUrlOk(url):
    try:
        with requests.session() as s:
            r = s.get(url)
            if r.status_code != 200:
                return False

    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
    else:
        return True   

def scrape_url(url, titles_to_match, titles_not_to_match):
    try:
        with requests.session() as s:
            r = s.get(url)
            if r.status_code != 200:
                print('s.get(url) with url', url, 'failed')
            soup = BeautifulSoup(r.content, 'html.parser')
            all_tr = soup.find(id='SearchResults').find_all('tr')
            for tr in all_tr:
                # get string
                res = tr.find(class_='detLink')
                if res is None: # table header has and should not have class attr detLink
                    continue
                href_str = tr.find(class_='detLink')['href'].lower()
                print('\n'+href_str)

                if href_str is not None and href_str not in glo_alreadyMatched:
                    if all(x in href_str for x in titles_to_match) and not any(x in href_str for x in titles_not_to_match):
                        sendEmail('url match:' + url, url)
                        print('email sent')
                        glo_alreadyMatched.append(href_str)
                
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))

def userInput():
    try:
        # URL
        need_url_input = True
        while need_url_input:
            url = input('Pirate-bay url (copy address bar link): ')
            print('checking url "' + url + '"')
            if not isUrlOk(url):
                print('Did not get a proper response from URL. Check it and try again')
            else:
                need_url_input = False

        # titles to match
        need_title_input = True
        while need_title_input:
            titles_to_match_str = input('\nTitles to look for (separate with comma with NO space between): ')
            # looking for spaces
            if titles_to_match_str.find(', ') != -1 or titles_to_match_str.find(' ,') != -1:
                print('Found spaces between comma. Redo')
            else:
                titles_to_match_list = titles_to_match_str.split(',')
                print('list of words that will be searched for:', titles_to_match_list)
                need_title_input = False

        need_unmatch_title_input = True
        while need_unmatch_title_input:
            default_titles_to_not_match_list = ['prelims', 'weigh-ins', 'preliminary', 'inside']
            titles_to_not_match_str = input('\nTitles NOT to look for (separate with comma). \nDefault: '+str(default_titles_to_not_match_list)+'. (Input will override; Enter will use Default): ')
            # looking for spaces
            if titles_to_not_match_str.find(', ') != -1 or titles_to_not_match_str.find(' ,') != -1:
                print('Found spaces between comma. Redo')
            else:
                if titles_to_not_match_str:
                    titles_to_not_match_list = titles_to_not_match_str.split(',')
                    print('list of words that will be searched for:', titles_to_not_match_list)
                    need_unmatch_title_input = False
                else:
                    titles_to_not_match_list = default_titles_to_not_match_list
                    print('list of words that will be searched for:', titles_to_not_match_list)
                    need_unmatch_title_input = False

        return url, titles_to_match_list, titles_to_not_match_list

    except Exception as e:
        print ('ERROR in function' ,inspect.stack()[0][3], ':', str(e))

def main():
    url, titles_to_match, titles_not_to_match = userInput()

    while True:
        scrape_url(url, titles_to_match, titles_not_to_match)

        print('sleeping for ' + str(seconds_to_sleep) + ' seconds')
        time.sleep(seconds_to_sleep)

main()

