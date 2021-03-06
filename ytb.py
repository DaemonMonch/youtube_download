#!/usr/bin/python3
import requests as r
import concurrent.futures
import json,time,random,mimetypes,sys,threading,os
import sum
from urllib.parse import urlparse,parse_qs,unquote

def get_video_size(url):
    m = {}
    info = r.head(url)
    content_length = info.headers.get('content-length') 
    m['size'] = int(content_length)
    m['mimetype'] = info.headers.get('content-type')
    m['rangeable'] = info.headers.get('accept-ranges')
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
            if not mime_type in ['.mp4']:
                continue
            size = info.get('size')
            if not max_f:
                max_f["url"] = url
                max_f["size"] = size
                max_f['mimetype'] = mime_type
                max_f['rangeable'] = info['rangeable']
                continue
            
            if max_f.get("size") < size:
                max_f["url"] = url
                max_f["size"] = size
                max_f['mimetype'] = mime_type
                max_f['rangeable'] = info['rangeable']
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

def _download(url,s,ra,filename):
    import sys
    headers = {'Range':"bytes={}".format(ra)} if ra else None
    res = r.get(url,stream=True,headers=headers)
    with open(filename, 'wb') as fd:
        for chunk in res.iter_content(chunk_size=65535):
            s.incr(65535)
            fd.write(chunk)
            sys.stdout.write('\r {:.2f}%'.format(s.get_ratio()))
            sys.stdout.flush()
        fd.flush()

def download(info):
    size = info.get('size')
    url = info.get('url')
    thread_num = 1 if size < 10485760 else  8
    partital_size =  size // thread_num
    ranges = []
    if thread_num > 1 and info.get('rangeable'):
        for i in range(0,thread_num):
            s = i * partital_size + (1 if i > 0 else 0)
            e = (i + 1) * partital_size if i + 1 < thread_num else size
            ranges.append("{}-{}".format(s,e))
    if len(ranges) == 0:
        file_info = [{'filename':vid}]
    else:
        file_info = []
        for rn in ranges:
            file_info.append({'filename':"{}-{}".format(vid,rn),'range':rn})
    fs = []
    s = sum.Sum(size)
    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_num) as executor:
        fs = [executor.submit(_download,url,s,fi.get('range'),fi.get('filename')) for fi in file_info]
    concurrent.futures.wait(fs)
    return map(lambda f:f.get("filename"),file_info)


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
    adaptive_fmts_encoded = content.get("url_encoded_fmt_stream_map")
    if not adaptive_fmts_encoded or len(adaptive_fmts_encoded) == 0:
        print("get video info fail")
        exit(-1)
    video_urls = parse_qs(adaptive_fmts_encoded[0]).get("url")
    print(video_urls)
    max_f = find_max_quality_url(map(lambda l: unquote(l),video_urls))
    videoname = get_filename(max_f.get('mimetype'))
    print(max_f)
    print(videoname)
    if not max_f:
        print("get video info fail")
        exit(-1)

    filenames = download(max_f)
    with open(videoname,"wb") as out:
        for filename in filenames:
            with open(filename,"rb") as fin:
                while True:
                    content = fin.read(65535)
                    if not content:
                        break
                    out.write(content)
            out.flush()
            os.unlink(filename)
    print("done!")                



if __name__ == "__main__":
    main()
