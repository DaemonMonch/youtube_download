#!/usr/bin/python3
# encoding=utf8
import requests as r
import json,time,random,mimetypes,sys
from urllib.parse import urlparse,parse_qs,unquote

url = sys.argv[1]
decode_url = urlparse(url)
vid = parse_qs(decode_url.query).get('v')[0]
mimetypes.init()
info_url = "http://www.youtube.com/get_video_info?video_id={}".format(vid)
info_resp = r.get(info_url)
content = info_resp.text
player_response_index = content.find("adaptive_fmts=")
if player_response_index < 0:
    print("no")
    exit(-1)
i=player_response_index
while True:
    if content[i] == "&":
        break
    i += 1  
s = content[player_response_index : i]
adaptive_fmts_quoted = s[s.index('=') + 1 : ]      
adaptive_fmts = unquote(adaptive_fmts_quoted)
fmts = adaptive_fmts.split("&")
if len(fmts) < 1:
    print('video info got fail')
    exit(1)
urls = []
for fmt in fmts:
    if fmt.find("url=") > -1:
        url = unquote(fmt[4:len(fmt)])
        urls.append(url)
if len(urls) == 0:
    print("video url not found")
    exit(-1)
max_f = {}
for f in urls:
    info = r.head(f)
    content_length = info.headers.get('content-length') 
    if not max_f:
        max_f['url'] = f
        max_f['_length'] = content_length
        continue
    if int(max_f.get('_length')) < int(content_length):
        max_f['url'] = f
        max_f['_length'] = content_length
#videoDetails = json.get('videoDetails')
#if not videoDetails:
#    print('video info got fail')
#    exit(1)
#title = videoDetails.get('title')
#print("\nvid:" + vid)
#print("title:" + title)
#mime_type = max_f.get('mimeType')
#if not mime_type:
#    print('video info got fail')
#    exit(1)
#type_index = mime_type.index(';')
#if type_index > -1:
#    mime_type = mime_type[0 : type_index + 1]
#ext = mimetypes.guess_extension(mime_type) or '.mp4'
filename = '{}.mp4'.format(vid or vid)
res = r.get(max_f.get('url'),stream=True)
cl = int(res.headers.get('content-length'))
sum = 0
with open(filename, 'wb') as fd:
    for chunk in res.iter_content(chunk_size=65535):
        sum += 65535
        fd.write(chunk)
        sys.stdout.write('\r {:.2f}%'.format(sum * 100 / cl))
        sys.stdout.flush()
    fd.flush()
print('\nDone!')
    
