import requests
server = 'http://127.0.0.1:5000/updatedb'

def check_urls():
    r = requests.get(server)
    return r

if __name__=='__main__':
    print(check_urls().text)
