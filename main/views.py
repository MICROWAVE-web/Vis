import time
import urllib.request
from datetime import datetime

import pytube
import validators
from django.http import HttpResponse, HttpResponseNotFound
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.http import require_http_methods
from pytube import YouTube
from youtube_dl import YoutubeDL


class IncorrectLink(Exception):
    pass


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
        try:
            assert validators.url(url)
            self.yt = YouTube(url)
        except AssertionError:
            raise IncorrectLink('Некорректный url')
        except Exception:
            raise IncorrectLink('Не удалось обработать видео с Ютуб')

    def streams(self):
        return [st.__dict__ for st in
                self.yt.streams.filter(subtype='mp4', progressive=True).order_by(
                    'resolution')]

    def audio_streams(self):
        return [st.__dict__ for st in
                self.yt.streams.filter(type='audio', mime_type='audio/mp4').order_by('abr')]


class VK(Social):
    def streams(self):
        output_streams = []
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
    is_correct = False
    output_streams = []
    for social_key in SOCIAL_LIST.keys():
        for domain in SOCIAL_LIST[social_key][0]:
            if domain in url:
                social_object = SOCIAL_LIST[social_key][-1](url)
                if social_object:
                    try:
                        output_streams = social_object.streams()
                        is_correct = True
                    except pytube.exceptions.VideoUnavailable:
                        print('video link is unvailuble')
                        is_correct = False
                    break

    serializable_streams = []
    if len(output_streams) != 0:
        for index, stream in enumerate(output_streams):
            serializable_streams.append(dict())
            for key in stream.keys():
                if isinstance(stream[key], (str, int, float)):
                    serializable_streams[index][key] = stream[key]
            serializable_streams[index]['filesize'] = urllib.request.urlopen(stream['url']).headers['Content-Length']
    return serializable_streams, is_correct


@require_http_methods(["POST"])
def validate_url(request):
    url = request.POST.get('url').strip().replace(' ', '')
    response = {
        'streams': general_streams(url),
    }
    return JsonResponse(response, safe=False, json_dumps_params={'ensure_ascii': False})


@require_http_methods(["GET"])
def waprfile(request):
    link = request.GET.get('link').replace('mozzarella', '&')
    title = request.GET.get('title')
    exp = request.GET.get('exp')
    try:
        assert link, 'Не хватает входных данных (link)'
        assert exp in ['mp3', 'mp4', '3gpp'], 'Не хватает входных данных (exp)'
        print('Получение данных...')

        data_request = urllib.request.urlopen(link)
        file_data = data_request.read()
        meta = data_request.info()
        print(meta)
        print('Данные получены.')
        if exp == 'mp4':
            response = HttpResponse(file_data, content_type='video/mp4')
        elif exp == 'mp3' or '3gpp':
            response = HttpResponse(file_data, content_type="video/3gpp")
        else:
            response = HttpResponse(file_data)
        if title is None:
            response[
                'Content-Disposition'] = f'attachment; filename="video-{datetime.now().strftime("%Y-%m-%d")}.{exp}"'
        else:
            response['Content-Disposition'] = f'attachment; filename="video-{title}.{exp}"'
        return response

    except AssertionError as err:
        return HttpResponseNotFound(f'<h1>Not enough entry data</h1>')
    except IOError:
        return HttpResponseNotFound('<h1>File not exist</h1>')


class Vis(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'main/main.html')
