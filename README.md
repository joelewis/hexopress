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

Project setup:  

Clone the repo `$ git clone https://github.com/joelewis/hexopress`  

Create a python virtual env and install python dependencies into it.  
`$ virtualenv --distribute venv`  
`$ . venv/bin/activate`  
`$ pip install -r requirements.txt`  

Rename `hexopress/sample_settings.py` to `hexopress/settings.py`  

Tweak the config to suit yours. 

Run Interface Server:  
`daphne hexopress.asgi:channel_layer -b 0.0.0.0 -p 8000`

Run workers for websockets/http handling:  
`python manage.py runworker -v 2`  

Run celery worker:  
`celery -A hexopress worker`

Now, pointing your browser to http://localhost:8000 should land it to your dev instance.
  
