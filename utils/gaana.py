import base64
import os
import urllib
from Crypto.Cipher import AES
from mutagen.mp4 import MP4, MP4Cover
from ffmpeg_progress_yield import FfmpegProgress
from tqdm import tqdm

DOWNLOAD_PATH = './Download/'


def unpad(s):
    return s[0 : -ord(s[-1])]


def decryptLink(message):
    IV = 'asd!@#!@#@!12312'.encode('utf-8')
    KEY = 'g@1n!(f1#r.0$)&%'.encode('utf-8')
    aes = AES.new(KEY, AES.MODE_CBC, IV)
    return unpad((aes.decrypt(base64.b64decode(message))).decode('utf-8'))


def download(url, name, ftitle):
    # ftitle = folder title
    # stream = ffmpeg.input(url)
    # stream = ffmpeg.output(stream, DOWNLOAD_PATH + name + '.m4a')
    # ffmpeg.run(stream)

    if not os.path.isdir(DOWNLOAD_PATH):
        os.mkdir(DOWNLOAD_PATH)

    path = DOWNLOAD_PATH + ftitle + '/'
    isdir = os.path.isdir(path)
    if not isdir:
        os.mkdir(path)

    cmd = ["ffmpeg", "-y", "-i", url, path + name + '.m4a']
    ff = FfmpegProgress(cmd)
    with tqdm(total=100, position=1, desc=name, bar_format='{desc:<30}{percentage:3.0f}%|{bar:50}{r_bar}') as pbar:
        for progress in ff.run_command_with_progress():
            pbar.update(progress - pbar.n)


def meta_data(song_data, key=None):
    path = None
    if key == 'album' or 'song':
        path = DOWNLOAD_PATH + song_data['album'] + '/'

    if key == 'playlist':
        path = DOWNLOAD_PATH + song_data['playlist_title'] + '/'

    # print('Writing MetaData....!')
    audio = MP4(path + song_data['title'] + '.m4a')
    audio['\xa9nam'] = song_data['title']
    audio['\xa9alb'] = song_data['album']
    audio['\xa9wrt'] = song_data['composer']
    audio['\xa9ART'] = song_data['artists']

    fd = urllib.request.urlopen(song_data['cover'])
    covr = MP4Cover(fd.read(), getattr(MP4Cover, 'FORMAT_JPEG'))
    fd.close()
    audio['covr'] = [covr]
    audio.save()


def get_song_data(data):
    encrypted_link = None
    if data['song']['songDetail']['tracks'][0]['urls']['high']:
        encrypted_link = data['song']['songDetail']['tracks'][0]['urls']['high']['message']
    elif data['song']['songDetail']['tracks'][0]['urls']['medium']:
        encrypted_link = data['song']['songDetail']['tracks'][0]['urls']['medium']['message']
    else:
        encrypted_link = data['song']['songDetail']['tracks'][0]['urls']['auto']['message']

    # metdata
    artists = data['song']['songDetail']['tracks'][0]['artist']
    song_metadata = {
        'title': data['song']['songDetail']['tracks'][0]['track_title'],
        'album_id': data['song']['songDetail']['tracks'][0]['track_title'],
        'album': data['song']['songDetail']['tracks'][0]['album_title'],
        'language': data['song']['songDetail']['tracks'][0]['language'],
        'duration': (
            str(int(data['song']['songDetail']['tracks'][0]['duration']) // 60)
            + ' min '
            + str(int(data['song']['songDetail']['tracks'][0]['duration']) % 60)
            + ' sec'
        ),
        'cover': data['song']['songDetail']['tracks'][0]['artwork_large'],
        'artists': [artist['name'] for artist in artists],
        'composer': data['song']['songDetail']['tracks'][0]['composer'][0]['name'],
        'url': decryptLink(encrypted_link),
    }
    return song_metadata


def get_albumb_data(data):
    tracks = data['album']['albumDetail']['tracks']
    album_data = {
        'language': data['album']['albumDetail']['tracks'][0]['language'],
        'year': data['album']['albumDetail']['release_year'],
        'tracks': [],
    }

    for track in tracks:
        tracks = {
            'album': data['album']['albumDetail']['tracks'][0]['album_title'],
            'title': track['track_title'],
            'composer': data['album']['albumDetail']['composers'][0]['name'],
            'duration': (str(int(track['duration']) // 60) + ' min ' + str(int(track['duration']) % 60) + ' sec'),
            'artists': [artist['name'] for artist in track['artist']],
            'cover': track['artwork_large'],
            'url': decryptLink(track['urls']['high']['message'])
            if track['urls']['high']['message']
            else track['urls']['auto']['message'],
        }
        album_data['tracks'].append(tracks)

    return album_data


def get_playlist_data(data):
    tracks = data['playlist']['playlistDetail']['tracks']
    playlist_data = []
    for track in tracks:
        tracks = {
            'playlist_title': data['playlist']['playlistDetail']['playlist']['title'],
            'album': track['album_title'],
            'title': track['track_title'],
            'duration': (str(int(track['duration']) // 60) + ' min ' + str(int(track['duration']) % 60) + ' sec'),
            'artists': [artist['name'] for artist in track['artist']],
            'cover': track['artwork_large'],
            'composer': track['artist'][0]['name'],
            'url': decryptLink(track['urls']['high']['message']),
            'year': track['release_date'].split('-')[0],
        }
        playlist_data.append(tracks)

    return playlist_data
