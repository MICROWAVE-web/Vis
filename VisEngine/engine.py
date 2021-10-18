import validators
from pytube import YouTube
from youtube_dl import YoutubeDL


class Social:
    def __init__(self, url=''):
        if validators.url(url):
            self.url = url


class Youtube(Social):
    def __init__(self, url=''):
        super().__init__(url)
        if validators.url(url):
            try:
                self.yt = YouTube(url)
            except Exception:
                self.yt = None
        else:
            self.yt = None

    def streams(self):

        return [st.__dict__ for st in self.yt.streams.filter(progressive=True)]

    def video_streams(self):
        return [st.__dict__ for st in self.yt.streams.filter(type='video', mime_type='video/mp4', progressive=True).order_by('resolution')]

    def audio_streams(self):
        return [st.__dict__ for st in self.yt.streams.filter(type='audio', mime_type='audio/mp4').order_by('abr')]


class VK(Social):
    def streams(self):
        output_streams = []
        with YoutubeDL() as ydl:
            info_dict = ydl.extract_info(self.url, download=False)
            for stream in info_dict['formats']:
                if str(stream.get('format_id')).startswith('cache') or str(stream.get('format_id')).startswith('url'):
                    output_streams.append(stream)
                elif stream.get('format_id') in [str(i) for i in range(1000)] and \
                        stream.get('ext') in ['m4a', 'mp4'] and stream.get('asr') and stream.get('fps') \
                        and not str(stream.get('format_id')).startswith('hls'):
                    output_streams.append(stream)
        return output_streams

class SoundCloud(Social):
    def streams(self):
        output_streams = []
        with YoutubeDL() as ydl:
            info_dict = ydl.extract_info(self.url, download=False)
            for stream in info_dict['formats']:
                if stream.get('format_id') == f'http_mp3_{stream.get("abr")}':
                    output_streams.append(stream)
        return output_streams


class FaceBook(Social):
    def streams(self):
        output_streams = []
        with YoutubeDL() as ydl:
            info_dict = ydl.extract_info(self.url, download=False)
            if info_dict.get('entries'):
                for stream in info_dict['entries'][0]['formats']:
                    if stream.get('acodec') == 'mp4a.40.5':  # аудио дорожка
                        output_streams.append(stream)
                    elif stream.get('format_id') in ['dash_sd_src',
                                                     'dash_sd_src_no_ratelimit', 'sd']:  # Порядке возростания качества
                        output_streams.append(stream)
            else:
                for stream in info_dict['formats']:
                    if stream.get('acodec') == 'mp4a.40.5':  # аудио дорожка
                        output_streams.append(stream)
                    elif stream.get('format_id') in ['dash_sd_src',
                                                     'dash_sd_src_no_ratelimit', 'sd']:  # Порядке возростания качества
                        output_streams.append(stream)
        return output_streams

    def video_streams(self):
        output_streams = []
        with YoutubeDL() as ydl:
            info_dict = ydl.extract_info(self.url, download=False)
            if info_dict.get('entries'):
                for stream in info_dict['entries'][0]['formats']:
                    if stream.get('format_id') in ['dash_sd_src',
                                                   'dash_sd_src_no_ratelimit', 'sd']:  # Порядке возростания качества
                        output_streams.append(stream)
            else:
                for stream in info_dict['formats']:
                    if stream.get('format_id') in ['dash_sd_src',
                                                   'dash_sd_src_no_ratelimit', 'sd']:  # Порядке возростания качества
                        output_streams.append(stream)
        return output_streams

    def audio_streams(self):
        output_streams = []
        with YoutubeDL() as ydl:
            info_dict = ydl.extract_info(self.url, download=False)
            if info_dict.get('entries'):
                for stream in info_dict['entries'][0]['formats']:
                    if stream.get('acodec') == 'mp4a.40.5':  # аудио дорожка
                        output_streams.append(stream)
            else:
                for stream in info_dict['formats']:
                    if stream.get('acodec') == 'mp4a.40.5':  # аудио дорожка
                        output_streams.append(stream)
        return output_streams


SOCIAL_LIST = {
    'FaceBook': (['fb.watch', 'www.facebook.com'], FaceBook),
    'SoundCloud': (['soundcloud.com'], SoundCloud),
    'VK': (['vk.com'], VK),
    'Youtube': (['youtu.be', 'www.youtube.com'], Youtube)
}

objects = [VK('https://vk.com/video?z=video-145643494_456247633'),
           Youtube('https://youtu.be/3DTjssGsUHk'),
           SoundCloud('https://soundcloud.com/nensiman/00sokkb3rjmv?si=2041f4cc0588465081f9421d13a63a69'),
           FaceBook('https://www.facebook.com/100068911394690/videos/419689926157530/')]


