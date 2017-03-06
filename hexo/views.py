import json
import os, io, subprocess, urllib
import datetime, dateutil.parser
import shutil, errno

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.template import loader
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from django.views import static

# models import
from django.contrib.auth.models import User
from hexo.models import *

# google auth related
from apiclient import discovery
from apiclient.http import MediaIoBaseDownload
import httplib2
from oauth2client import client

import pypandoc

def index(request):
    """
    Index page!
    """
    if not request.user.is_authenticated():
        template = loader.get_template('index.html')
        return HttpResponse(template.render({
            "user": {},
        }, request))
    else:
        template = loader.get_template('loggedin_index.html')
        blog = BlogSettings.objects.get(user=request.user)
        googleuser = GoogleUser.objects.get(user=request.user)
        print request.user.first_name
        print 1 if request.user.first_name else 0
        return HttpResponse(template.render({
            "user": {
                "email": request.user.email,
                "name": request.user.first_name,
                "username": request.user.username,
                "accountinfo_filled": 1 if request.user.first_name else 0,
            },
            "blog": {
                "title": blog.title or '',
                "subtitle": blog.subtitle or '',
                "description": blog.description or '',
                "is_generated": 1 if googleuser.is_site_generated else 0,
            }
        }, request))


def get_credentials(googleuser):
    return client.AccessTokenCredentials(googleuser.access_token, 'web client')
    
def get_drive_service(googleuser):
    cred = get_credentials(googleuser)
    http_auth = cred.authorize(httplib2.Http())
    drive_service = discovery.build('drive', 'v3', http=http_auth)
    return drive_service
    
def get_plus_service(googleuser):
    cred = client.AccessTokenCredentials(googleuser.access_token, 'web client')
    http_auth = cred.authorize(httplib2.Http())
    plus_service = discovery.build('plus', 'v1', http=http_auth)
    return plus_service

@csrf_exempt
def google_login(request): 
    """
    1. Receive google token from google's signin callback.
    2. Get token's email & get/create a user against it.
    3. Mark the user as logged in.
    """
    # Exchange auth code for access token, refresh token, and ID token
    auth_code = request.POST['authCode']

    credentials = client.credentials_from_clientsecrets_and_code(
        settings.CLIENT_SECRET_FILE,
        ['https://www.googleapis.com/auth/drive', 'profile', 'email'],
        auth_code)
    email = credentials.id_token['email']
    guser_id = credentials.id_token['sub']
    username = email.split('@')[0]
    try: 
        user = User.objects.get(email=email)
    except: 
        user = User(username=username, email=email)
        user.save()

    googleuser, created = GoogleUser.objects.get_or_create(user=user)
    googleuser.access_token = credentials.access_token
    googleuser.refresh_token = credentials.refresh_token
    googleuser.guser_id = guser_id
    googleuser.save()
    login(request, user)
    return JsonResponse({"success": True})
    
def user_logout(request):
    """
    logout user
    """
    logout(request)
    return HttpResponseRedirect('/')


def get_folder(service):
    matching_folders = service.files().list(q="(mimeType='application/vnd.google-apps.folder') and (name='blog')").execute()
    
    if len(matching_folders['files']) > 0:
        return matching_folders['files'][0]['id']
    return None

def get_files_from_folder(service, folder_id):
    files = service.files().list(
        q="('{0}' in parents) and (mimeType = 'application/vnd.google-apps.document')".format(folder_id),
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
                "title": file_name,
                "date": created_time_str,
                "categories": ""
            })
            
            outputfile = '{0}/{1}-{2}.markdown'.format(md_dir, 
                created_time.strftime('%Y-%m-%d'),
                slugify(file_name))
                
            # convert file
            pypandoc.convert_file(
                '{0}/{1}.docx'.format(docx_dir, file_name), 
                'md', 
                outputfile=outputfile)
                    
            # prepend yaml_matter to converted file
            # TODO: do this in-place, rather than in-memory
            prepend2file(outputfile, yaml_matter)
        else:
            # handle error
            pass
    return callback

def download_docx_files(user, service, files):
    batch = service.new_batch_http_request()
    
    for file_meta in files:
        callback = get_callback(file_meta, user)
        # callback as closure
        req = service.files().export_media(fileId=file_meta['id'], mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        batch.add(req, callback=callback)
    
    batch.execute()

def copydir(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else:
            # directory already exists. it's ok to pass.
            pass

def create_octopress(user):
    googleuser = GoogleUser.objects.get(user=user)
    
    copydir(settings.OCTOPRESS_CLONE, '{0}/{1}/octopress'.format(
        settings.BLOG_DIR_ROOT,
        user.email
    ))
    
    # configure blog
    title = user.email
    subtitle = 'Random Thoughts'
    author = user.email    
    
    config_file_template = loader.get_template('config.yml.html')
    config_file = config_file_template.render({
        "title": title,
        "subtitle": subtitle,
        "author": author,
        "username": user.username
    })
    write2file('{0}/{1}/octopress/_config.yml'.format(
        settings.BLOG_DIR_ROOT,
        user.email
    ), config_file)
    
    googleuser.is_site_generated = True
    googleuser.save()
        
@login_required
def refresh_blog(request):
    """
    1. get files from the user's 'blog' drive folder
    2. convert those files to markdown and collect them 
       under .../conversions/email/md/
    """
    googleuser = GoogleUser.objects.get(user=request.user)
    drive_service = get_drive_service(googleuser)
    
    template = loader.get_template('refreshblog.html')
    response = ''
    
    try: 
        # matching folder may not be present. throw info in such case
        folder_id = get_folder(drive_service)
        if not folder_id:
            # handle error
            response = 'folder not present'
        
        # get all google docs files from the folder
        files = get_files_from_folder(drive_service, folder_id)
        response = files
        download_docx_files(request.user, drive_service, files['files'])
        
    except client.AccessTokenCredentialsError:
        response = 'access token expired'
        return HttpResponseRedirect('/googlelogin?next=/refreshblog')
    
    return HttpResponse(template.render({
        "user": request.user,
        "response": response
    }, request))
    
@login_required
def generate_blog(request):
    """
    1. generate octopress blog setup, if not present.
    2. read all markdown files from .../conversions/email/md/
    3. create post source out of each file & move them to their octopress source
    4. return url for that user's octopress public folder
    """
    googleuser = GoogleUser.objects.get(user=request.user)
    ensure_dir('{0}/{1}'.format(settings.BLOG_DIR_ROOT, request.user.email))
    
    googleuser.is_site_generated = False
    if not googleuser.is_site_generated:
        # call routine to generate octopress for that user
        create_octopress(request.user)
    
    # copy source files
    shutil.rmtree('{0}/{1}/octopress/source/_posts'.format(
                        settings.BLOG_DIR_ROOT, request.user.email))
    copydir('{0}/{1}/md'.format(settings.CONVERSION_DIR_ROOT,
                                    request.user.email), 
            '{0}/{1}/octopress/source/_posts'.format(settings.BLOG_DIR_ROOT,
                                    request.user.email))
    
    # run rake generate
    print '{0}/{1}/octopress'.format(
                            settings.BLOG_DIR_ROOT, request.user.email)
    subprocess.call('rake generate', 
                        cwd='{0}/{1}/octopress'.format(settings.BLOG_DIR_ROOT, 
                                                        request.user.email), 
                        shell=True)
    
    return JsonResponse({
        "url": "/@{0}/".format(request.user.username)
    })

def serve_blog(request, username, path):
    bloguser = User.objects.get(username=username)
    print path
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
                redirect_uri='http://localhost:8000/oauth2callback')
    flow.params['state'] = urllib.urlencode(request.GET)
    # flow.params['access_type'] = 'offline'         # offline access
    # flow.params['include_granted_scopes'] = 'true'   # incremental auth
    auth_uri = flow.step1_get_authorize_url()
    return HttpResponseRedirect(auth_uri)

def oauth2callback(request):
    auth_code = request.GET['code']
    print auth_code
    credentials = client.credentials_from_clientsecrets_and_code(
        settings.CLIENT_SECRET_FILE,
        ['https://www.googleapis.com/auth/drive', 'profile', 'email'],
        auth_code,
        redirect_uri='http://localhost:8000/oauth2callback')
    # credentials = flow.step2_exchange(auth_code)
    print credentials.id_token
    email = credentials.id_token['email']
    guser_id = credentials.id_token['sub']
    print credentials.id_token
    username = email.split('@')[0]
    try: 
        user = User.objects.get(email=email)
    except: 
        user = User(username=username, email=email)
        user.save()

    googleuser, created = GoogleUser.objects.get_or_create(user=user)
    googleuser.access_token = credentials.access_token
    googleuser.refresh_token = credentials.refresh_token
    googleuser.guser_id = guser_id
    googleuser.save()
    login(request, user)
    state = request.GET.get('state')
    if state:
        param = state
    else:
        param = ''
    redirect_uri = '/?' + param
    return HttpResponseRedirect(redirect_uri)

@login_required
@csrf_exempt
def blog_settings(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        subtitle = request.POST.get('subtitle')
        description = request.POST.get('description')
        
        blogsettings, created = BlogSettings.objects.get_or_create(
            user=request.user)
        blogsettings.title = title
        blogsettings.subtitle = subtitle
        blogsettings.description = description
        blogsettings.save()

    return HttpResponseRedirect('/?task=generate_blog')

@login_required
@csrf_exempt
def account_settings(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        name = request.POST.get('name')

        print request.POST
        if not len(username):
            return HttpResponseRedirect('/app/settings/account')
        
        user = request.user
        try:
            user.username = username
            user.first_name = name
            user.save()
        except:
            return HttpResponseRedirect('/app/settings/account')
    
    return HttpResponseRedirect('/?task=generate_blog')
