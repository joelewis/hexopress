from __future__ import absolute_import
import time
import json
import os, io, subprocess
import datetime, dateutil.parser
import shutil, errno
import logging
import re

from django.template import loader
from django.conf import settings

from hexopress.celery import app

#utils 
from django.utils.text import slugify
from hexo.ReplyChannel import ReplyChannel

# models import
from hexo.models import *

# google auth related
from apiclient import discovery
from apiclient.http import MediaIoBaseDownload
import httplib2
from oauth2client import client

import pypandoc

# utils
def get_credentials(googleuser):
    return client.AccessTokenCredentials(googleuser.access_token, 'web client')
    
def get_drive_service(googleuser):
    cred = get_credentials(googleuser)
    http_auth = cred.authorize(httplib2.Http())
    drive_service = discovery.build('drive', 'v3', http=http_auth)
    return drive_service

def get_folder(service):
    matching_folders = service.files().list(q="(mimeType='application/vnd.google-apps.folder') and (name='hexopress')").execute()
    
    if len(matching_folders['files']) > 0:
        return matching_folders['files'][0]['id']
    else:
        file_metadata = {
            'name' : 'hexopress',
            'mimeType' : 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=file_metadata,
                                            fields='id').execute()
        return folder.get('id')

def get_files_from_folder(service, folder_id):
    files = service.files().list(
        q="('{0}' in parents) and (mimeType = 'application/vnd.google-apps.document')".format(folder_id),
        fields="files(id, name, createdTime)").execute()
    return files
    
def get_md_files_from_folder(service, folder_id):
    files = service.files().list(
        q="('{0}' in parents) and (mimeType = 'text/markdown')".format(folder_id),
        fields="files(id, name, createdTime)").execute()
    return files

def ensure_dir(path):
    user_dir_exist = os.path.exists(path)
    if not user_dir_exist:
        # create user dir
        os.makedirs(path)

def prepend2file(outfile, content):
    with io.open(outfile, 'r+', encoding="utf-8") as f:
        prev_content = f.read()
        f.seek(0, 0)
        f.write(content + '\n' + prev_content)
        
def write2file(outfile, content):
    with open(outfile, 'w') as f:
        f.write(content)

def remove_extn(filename):
    return filename.split('.')[0]

def get_md_callback(file_meta, user):
    def callback(request_id, response, exception):
        if exception is None:
            file_name = file_meta['name'].replace(' ', '-')
            file_name = remove_extn(file_name)
            created_time_str = file_meta['createdTime']
            created_time = dateutil.parser.parse(created_time_str)

            md_dir = '{0}/{1}/md'.format(settings.CONVERSION_DIR_ROOT,
                                         user.email)
            ensure_dir(md_dir)

            outputfile = '{0}/{1}-{2}.markdown'.format(md_dir,
                                              created_time.strftime('%Y-%m-%d'),
                                              slugify(file_name))

            # write response to a md file
            f = open(outputfile, 'w+')
            f.write(response)
            f.close()

            template = loader.get_template('post_header_template.html')
            yaml_matter = template.render({
                "title": remove_extn(file_meta['name']),
                "date": created_time_str,
                "categories": ""
            })

            prepend2file(outputfile, yaml_matter)
        else:
            pass
    return callback

def get_callback(file_meta, user):
    def callback(request_id, response, exception):
        if exception is None:
            file_name = file_meta['name'].replace(' ', '-')
            created_time_str = file_meta['createdTime']
            created_time = dateutil.parser.parse(created_time_str)
            
            
            docx_dir = '{0}/{1}/docx'.format(settings.CONVERSION_DIR_ROOT,
                                                user.email)
            ensure_dir(docx_dir)
                
            # write response to a docx file
            f = open('{0}/{1}.docx'.format(docx_dir, file_name), 'w+')
            f.write(response)
            f.close()
            
            md_dir = '{0}/{1}/md'.format(settings.CONVERSION_DIR_ROOT,
                                            user.email)
            ensure_dir(md_dir)
            
            # construct yaml matter
            template = loader.get_template('post_header_template.html')
            yaml_matter = template.render({
                "title": file_meta['name'],
                "date": created_time_str,
                "categories": ""
            })
            
            outputfile = '{0}/{1}-{2}.markdown'.format(md_dir, 
                created_time.strftime('%Y-%m-%d'),
                slugify(file_name))

            outputmedia = '{0}/{1}/octopress/source/images'.format(settings.BLOG_DIR_ROOT, user.email)
            
            # convert file
            pypandoc.convert_file(
                '{0}/{1}.docx'.format(docx_dir, file_name),
                'md',
                outputfile=outputfile,
                extra_args=['--extract-media='+outputmedia])

            # replace links
            with open(outputfile, 'r') as f:
                content = f.read()

            # reset path to proper http path
            content = content.replace(outputmedia, '/images')
            # also remove image size info injected by pandoc
            rule = re.compile("(!\[\]\\(.*?\\))({.*?})", re.MULTILINE|re.DOTALL)
            content = rule.sub(r'\1', content)

            # understand code blocks


            with open(outputfile, 'w') as f:
                f.write(content)

            # prepend yaml_matter to converted file
            # TODO: do this in-place, rather than in-memory
            prepend2file(outputfile, yaml_matter)
        else:
            # handle error
            pass
    return callback

def clean_conversion_dir(user):
    docx_dir = '{0}/{1}/docx'.format(settings.CONVERSION_DIR_ROOT,
                                     user.email)
    md_dir = '{0}/{1}/md'.format(settings.CONVERSION_DIR_ROOT,
                                 user.email)
    if os.path.exists(docx_dir):
        shutil.rmtree(docx_dir)
    if os.path.exists(md_dir):
        shutil.rmtree(md_dir)

def download_docx_files(user, service, files):
    batch = service.new_batch_http_request()
    for file_meta in files:
        callback = get_callback(file_meta, user)
        # callback as closure
        req = service.files().export_media(
            fileId=file_meta['id'],
            mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        batch.add(req, callback=callback)

    batch.execute()


def download_md_files(user, service, files):
    for file_meta in files:
        file_id = file_meta['id']
        callback = get_md_callback(file_meta, user)
        # callback as closure
        req = service.files().get_media(fileId=file_meta['id'])
        try:
            resp = req.execute()
            callback(None, resp, None)
        except:
            # fail silently
            # Father, forgive me for I have sinned.
            pass

def copydir(src, dst):
    print "copying {0} to {1}".format(src, dst)
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else:
            # directory already exists. it's ok to pass.
            print "Couldn't copy {0} to {1}".format(src, dst)
            print exc
            pass

def refresh_config(user):
    title = user.first_name + "'s Blog"
    subtitle = "Thoughts, Musings & Stories"
    description = ""
    author = user.first_name 

    if BlogSettings.objects.filter(user=user).exists():
        blogsettings = BlogSettings.objects.get(user=user)
        title = blogsettings.title or title
        subtitle = blogsettings.subtitle or subtitle
        description = blogsettings.description or description
        ga_id = blogsettings.ga_id or ""

    # configure blog
    config_file_template = loader.get_template('config.yml.html')
    config_file = config_file_template.render({
        "title": title,
        "subtitle": subtitle,
        "author": author,
        "username": user.username,
        "description": description,
        "ga_id": ga_id
    })
    write2file('{0}/{1}/octopress/_config.yml'.format(
        settings.BLOG_DIR_ROOT,
        user.email
    ), config_file)

def create_octopress(user):
    print "creating octopress for user " + user.email
    googleuser = GoogleUser.objects.get(user=user)
    # copydir(settings.OCTOPRESS_CLONE, '{0}/{1}/octopress'.format(
    #     settings.BLOG_DIR_ROOT,
    #     user.email
    # ))
    # SINCE shutil.copytree was behaving erratically, falling back to rsync for now. We'll figure out the problem later
    user_octopress_dir = '{0}/{1}/octopress'.format(settings.BLOG_DIR_ROOT, user.email)
    ensure_dir(user_octopress_dir)
    rsync_command = 'rsync -r {0}/ {1}'.format(settings.OCTOPRESS_CLONE,  user_octopress_dir)
    print "executing: " + rsync_command
    subprocess.call(rsync_command, shell=True)

    refresh_config(user)

    googleuser.is_site_generated = True
    googleuser.save()

def serve_blog(request, username, path):
    bloguser = User.objects.get(username=username)
    if path.endswith('/') or not path: 
        path = path + '/index.html'
    else:
        # append '/', if check if dir exists
        if  os.path.isdir('{0}/{1}/octopress/public/{2}'.format(
                                settings.BLOG_DIR_ROOT,
                                bloguser.email,
                                path)):
            path = path + '/index.html'
    # if path doesn't end with '/', check if a directory or file exist in path
    return static.serve(request, 
                path,
                document_root=settings.BLOG_DIR_ROOT+'/'+bloguser.email+'/octopress/public/')


def refresh_accesstoken(request):
    flow = client.flow_from_clientsecrets(
                settings.CLIENT_SECRET_FILE,
                scope='https://www.googleapis.com/auth/drive profile email',
                redirect_uri=settings.HOST_ADDR+'/oauth2callback')
    flow.params['state'] = request.GET.get('next') or '/'
    # flow.params['access_type'] = 'offline'         # offline access
    # flow.params['include_granted_scopes'] = 'true'   # incremental auth
    auth_uri = flow.step1_get_authorize_url()
    return HttpResponseRedirect(auth_uri)

@app.task
def respond_in_three(user_id, channel_id, message):
    reply_channel = ReplyChannel(channel_id)
    time.sleep(1)
    reply_channel.send('respond_in_three', message)
    time.sleep(3)
    reply_channel.send('respond_in_three', message)
    reply_channel.send('respond_in_three', message)

@app.task
def generate_blog(user_id, channel_id, message):
    """
    1. get files from the user's 'blog' drive folder
    2. convert those files to markdown and collect them 
       under .../conversions/email/md/
    """
    reply_channel = ReplyChannel(channel_id)
    user = User.objects.get(id=user_id)
    googleuser = GoogleUser.objects.get(user=user)
    drive_service = get_drive_service(googleuser)

    reply_channel.send('blog_generation_initiated', {})
    try:
        # matching folder may not be present. throw info in such case
        folder_id = get_folder(drive_service)
        # get all google docs files from the folder
        files = get_files_from_folder(drive_service, folder_id)
        md_files = get_md_files_from_folder(drive_service, folder_id)
        reply_channel.send('blog_generation_progress', {"progress": 40})
        response = files
        clean_conversion_dir(user)
        download_docx_files(user, drive_service, files['files'])
        download_md_files(user, drive_service, md_files['files'])
        reply_channel.send('blog_generation_progress', {"progress": 60})
        copy2octopress(reply_channel, googleuser)
    except client.AccessTokenCredentialsError:
        reply_channel.send('access_token_expired', {})

def copy2octopress(reply_channel, googleuser):
    """
    1. generate octopress blog setup, if not present.
    2. read all markdown files from .../conversions/email/md/
    3. create post source out of each file & move them to their octopress source
    4. return url for that user's octopress public folder
    """

    user = googleuser.user
    user_octopress_dir = '{0}/{1}/octopress'.format(settings.BLOG_DIR_ROOT, user.email)
    ensure_dir(user_octopress_dir)
    googleuser.is_site_generated = False
    if not googleuser.is_site_generated:
        # call routine to generate octopress for that user
        create_octopress(user)
    

    # refresh config
    refresh_config(user)

    # remove previous source posts
    posts_src_dir = '{0}/{1}/octopress/source/_posts'.format(
        settings.BLOG_DIR_ROOT, user.email)

    if os.path.exists(posts_src_dir):
        shutil.rmtree(posts_src_dir)

    # copy source files
    copydir('{0}/{1}/md'.format(settings.CONVERSION_DIR_ROOT,
                                user.email),
            '{0}/{1}/octopress/source/_posts'.format(settings.BLOG_DIR_ROOT,
                                                     user.email))

    reply_channel.send('blog_generation_progress', {"progress": 80})

    # clean conversion directory to free some space
    clean_conversion_dir(user)
    # run rake generate

    subprocess.call('bundle exec rake generate',
                    cwd='{0}/{1}/octopress'.format(settings.BLOG_DIR_ROOT,
                                                   user.email),
                    shell=True)
    reply_channel.send('blog_generation_progress', {"progress": 100})
    reply_channel.send('blog_generated', {})


@app.task
def fetch_blog_status(user_id, channel_id, message):
    """
    returns blog status
    """
    reply_channel = ReplyChannel(channel_id)
    user = User.objects.get(id=user_id)
    googleuser = GoogleUser.objects.get(user=user)

    reply_channel.send('blog_status_fetched', {"generated": googleuser.is_site_generated})


# @app.task
# def install_theme(user_id, chanel_id, message):
#     """
#     install theme into user's octopress instance.
#     """
#     git_url = message["data"]["theme_url"]
