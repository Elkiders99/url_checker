import requests
server = 'http://127.0.0.1:5000'

def post_url_for_check(url):
    payload = {'url':url}
    r = requests.post(server,data=payload)
    return r

if __name__=='__main__':
    import sys
    url = sys.argv[1]
    print(post_url_for_check(url).text)
