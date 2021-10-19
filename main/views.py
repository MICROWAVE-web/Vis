import pytube
import requests
import validators
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from pytube import YouTube
from youtube_dl import YoutubeDL


class Social:
    def __init__(self, url=''):
        if validators.url(url):
            self.url = url

    def __bool__(self):
        if self.url != '':
            return True
        return False


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
        return [st.__dict__ for st in self.yt.streams.filter(type='video', mime_type='video/mp4',
                                                             progressive=True).order_by(
            'resolution')]

    def audio_streams(self):
        return [st.__dict__ for st in
                self.yt.streams.filter(type='audio', mime_type='audio/mp4').order_by('abr')]


class VK(Social):
    def streams(self):
        output_streams: list
        with YoutubeDL() as ydl:
            info_dict = ydl.extract_info(self.url, download=False)
            for stream in info_dict['formats']:
                if str(stream.get('format_id')).startswith('cache') or str(
                        stream.get('format_id')).startswith('url'):
                    output_streams.append(stream)
                elif stream.get('format_id') in [str(i) for i in range(1000)] and \
                        stream.get('ext') in ['m4a', 'mp4'] and stream.get('asr') and stream.get(
                    'fps') \
                        and not str(stream.get('format_id')).startswith('hls'):
                    output_streams.append(stream)
        return output_streams


class SoundCloud(Social):
    def streams(self):
        output_streams: list
        with YoutubeDL() as ydl:
            info_dict = ydl.extract_info(self.url, download=False)
            for stream in info_dict['formats']:
                if stream.get('format_id') == f'http_mp3_{stream.get("abr")}':
                    output_streams.append(stream)
        return output_streams


class FaceBook(Social):
    def streams(self):
        output_streams: list
        with YoutubeDL() as ydl:
            info_dict = ydl.extract_info(self.url, download=False)
            if info_dict.get('entries'):
                for stream in info_dict['entries'][0]['formats']:
                    if stream.get('acodec') == 'mp4a.40.5':  # аудио дорожка
                        output_streams.append(stream)
                    elif stream.get('format_id') in ['dash_sd_src',
                                                     'dash_sd_src_no_ratelimit',
                                                     'sd']:  # Порядке возростания качества
                        output_streams.append(stream)
            else:
                for stream in info_dict['formats']:
                    if stream.get('acodec') == 'mp4a.40.5':  # аудио дорожка
                        output_streams.append(stream)
                    elif stream.get('format_id') in ['dash_sd_src',
                                                     'dash_sd_src_no_ratelimit',
                                                     'sd']:  # Порядке возростания качества
                        output_streams.append(stream)
        return output_streams

    def video_streams(self):
        output_streams: list
        with YoutubeDL() as ydl:
            info_dict = ydl.extract_info(self.url, download=False)
            if info_dict.get('entries'):
                for stream in info_dict['entries'][0]['formats']:
                    if stream.get('format_id') in ['dash_sd_src',
                                                   'dash_sd_src_no_ratelimit',
                                                   'sd']:  # Порядке возростания качества
                        output_streams.append(stream)
            else:
                for stream in info_dict['formats']:
                    if stream.get('format_id') in ['dash_sd_src',
                                                   'dash_sd_src_no_ratelimit',
                                                   'sd']:  # Порядке возростания качества
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


def general_streams(url):
    output_streams = []
    for social_key in SOCIAL_LIST.keys():
        for domain in SOCIAL_LIST[social_key][0]:
            if domain in url:
                social_object = SOCIAL_LIST[social_key][-1](url)
                if social_object:
                    try:
                        output_streams = social_object.audio_streams()
                    except pytube.exceptions.VideoUnavailable:
                        print('video link is unvailuble')
                    break

    serializable_streams = []
    if len(output_streams) != 0:
        for index, stream in enumerate(output_streams):
            serializable_streams.append(dict())
            for key in stream.keys():
                if isinstance(stream[key], (str, int, float)):
                    serializable_streams[index][key] = stream[key]
    return serializable_streams


def validate_url(request):
    url = request.GET.get('url').strip().replace(' ', '')
    is_actual = (False, 'Внутрення ошибка')
    try:
        response = requests.head(url)
        if str(response.status_code)[0] in ['3', '2'] or str(response.status_code) == '418':
            is_actual = (True, 'Успешно')
        else:
            is_actual = (False, 'Не действительна')
    except Exception as e:
        is_actual = (False, 'Ошибка соединения')
    response = {
        'is_actual': is_actual,
        'streams': general_streams(url),
    }
    return JsonResponse(response, safe=False, json_dumps_params={'ensure_ascii': False})


class Vis(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'main/main.html')
