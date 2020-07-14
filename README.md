# url_checker

Runs a small server that will wait for client requests to check a URL until it comes up. Once it does a notification is sent to the desktop.


## Installation

Create a virtual environment with python>=3.6


Install requirements

>pip install -r requirements.txt

run the server

>python run.py

## Usage

Add urls that you want to check

>web_check \<url\>
 
That's it! you will be notified!

## Notifications

I'm using notify-send to send desktop notifications. 

If you are using a custom i3 with i3-blocks, just through the `block_web_check.py` in your PATH and call it from your `i3-blocks/config` using signal 15 (you can change the used signal in the server config file)

\[block_web_check.py\]
command=block_web_check.py
signal=15

