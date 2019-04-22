#!/usr/bin/python3
import requests as r
import concurrent.futures
import json,time,random,mimetypes,sys
from urllib.parse import urlparse,parse_qs,unquote

def get_video_size(url):
    m = {}
    info = r.head(url)
    content_length = info.headers.get('content-length') 
    m['size'] = int(content_length)
    m['mimetype'] = info.headers.get('content-type')
    return m

def find_max_quality_url(urls):
    max_f = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_url = {executor.submit(get_video_size,url):url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            info = {}
            try:
                info = future.result()
            except Exception as e:
                print("get exception while get size on url {},{}".format(url,e))
            if not  info:
                continue
            mime_type = mimetypes.guess_extension(info.get("mimetype"))  
            if not mime_type in ['.mp4','.webm']:
                continue
            size = info.get('size')
            if not max_f:
                max_f["url"] = url
                max_f["size"] = size
                max_f['mimetype'] = mime_type
                continue
            
            if max_f.get("size") < size:
                max_f["url"] = url
                max_f["size"] = size
                max_f['mimetype'] = mime_type
    return max_f                

def get_filename(mime_type):
    player_response = content.get("player_response")  
    if not player_response or len(player_response) == 0:
        print('video info got fail')
        exit(1)
    json_obj = json.loads(unquote(player_response[0]))
    videoDetails = json_obj.get('videoDetails')
    if not videoDetails:
        print('video info got fail')
        exit(1)
    title = videoDetails.get('title')
    print("\nvid:" + vid)
    print("title:" + title)
    
    filename = '{}{}'.format(title or vid,mime_type)
    return filename


def main():
    global content 
    global vid
    url = sys.argv[1]
    decode_url = urlparse(url)
    vid = parse_qs(decode_url.query).get('v')[0]
    mimetypes.init()
    info_url = "http://www.youtube.com/get_video_info?video_id={}".format(vid)
    info_resp = r.get(info_url)
    content = parse_qs(info_resp.text)
    adaptive_fmts_encoded = content.get("adaptive_fmts")
    if not adaptive_fmts_encoded or len(adaptive_fmts_encoded) == 0:
        print("get video info fail")
        exit(-1)
    #filename = get_filename()  
    video_urls = parse_qs(adaptive_fmts_encoded[0]).get("url")
    # for video_url in map(unquote,video_urls):
        # print(video_url)  
    max_f = find_max_quality_url(video_urls)
    filename = get_filename(max_f.get('mimetype'))
    print(max_f)
    print(filename)

if __name__ == "__main__":
    main()
