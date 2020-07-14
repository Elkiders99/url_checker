import requests

def return_list():
    ls = requests.get('http://127.0.0.1:5000/ls').text
    print(ls)

if __name__=='__main__':
    return_list()
