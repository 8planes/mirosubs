import re 

youtube_url_pattern = re.compile(r'youtube.com/.*?v[/=](?P<video_id>[\w-]+)')

def get_video_id(url):
    result = youtube_url_pattern.search(url)
    if result:
        return result.group('video_id')