# hexopress
A tiny blogging platform that lets you write posts in Google Docs and syncs with a Google Drive directory.

This project is directly based upon the amazing [Octopress](http://octopress.org) project. However, I wanted a way to keep writing my posts in Google Docs, which is a good place to write & retain blog posts, and publish a Octopress blog out them. This project is a way forward, towards scratching that itch.   

## What is HexoPress?
HexoPress is a web layer that authenticates the user with google, takes their blog posts from a folder in their google drive, generate a static blog out of it and serves them at a URL.

## Dev Setup
Install dependencies:
* Pandoc - http://pandoc.org/
* Ruby - http://rvm.io/
* Git - https://git-scm.com/
* Bundler - `gem install bundler`
* Octopress - http://octopress.org
* Redis - http://redis.org

### Project Setup:  

Clone the repo `$ git clone https://github.com/joelewis/hexopress`  

Create a python virtual env and install python dependencies into it.  
`$ virtualenv --distribute venv`  
`$ . venv/bin/activate`  
`$ pip install -r requirements.txt`  

Setup an Octopress instance - [http://octopress.org/docs/setup/](http://octopress.org/docs/setup/).

Rename `hexopress/sample_settings.py` to `hexopress/settings.py`

Edit `settings.py` to suit yours.

### Run Server

Run Interface Server:  
`daphne hexopress.asgi:channel_layer -b 0.0.0.0 -p 8000`

Run workers for websockets/http handling:  
`python manage.py runworker -v 2`  

Run celery worker:  
`celery -A hexopress worker` 

Now, pointing your browser to http://localhost:8000 should land it to your dev instance.

### Production setup

Edit settings.py to match your production config especially `settings.ALLOWED_HOSTS, settings.HOST and settings.CLIENT_SECRET (for google auth)`
Use a process manager like supervisord to manage your processes. 

Sample supervisord config
```
[program:daphne]
command = sh daphne.sh
stdout_logfile = /home/username/daphne.log
redirect_stderr = true
directory = /home/username/hexopress

[program:worker]
command = sh worker.sh
stdout_logfile = /home/username/worker.log
redirect_stderr = true
directory = /home/username/hexopress

[program:celery]
command = sh celery.sh
stdout_logfile = /home/username/celery.log
redirect_stderr = true
directory = /home/username/hexopress
``` 

Make sure to run `python manage.py migrate` once before starting the server. Without this your database will have no tables created yet. 




  
