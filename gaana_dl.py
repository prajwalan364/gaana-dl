import argparse
from utils.parser import parse_page
from utils.gaana import get_song_data, get_albumb_data, download, meta_data, get_playlist_data


def main():
    arg_parser = argparse.ArgumentParser(description="Gaana Music Downloader")
    arg_parser.add_argument("-s", dest="song", help="Enter the song url")
    arg_parser.add_argument("-a", dest="album", help="Enter album url")
    arg_parser.add_argument("-p", dest="playlist", help="Enter playlist url")
    args = arg_parser.parse_args()

    if not (args.song or args.album or args.playlist):
        arg_parser.error("No Action Requested..!,  add -h for help")

    if args.song:
        if "https://gaana.com/song/" not in args.song:
            arg_parser.error("Wrong Url")
        raw_data = parse_page(args.song)
        song_data = get_song_data(raw_data)
        download(song_data['url'], song_data['title'], song_data['album'])
        meta_data(song_data, key='song')

    if args.album:
        if "https://gaana.com/album/" not in args.album:
            arg_parser.error("Wrong Url")
        raw_data = parse_page(args.album)
        album_data = get_albumb_data(raw_data)
        for song in album_data['tracks']:
            download(song['url'], song['title'], song['album'])
            meta_data(song, key='album')

    if args.playlist:
        if "https://gaana.com/playlist/" not in args.playlist:
            arg_parser.error("Wrong Url")
        raw_data = parse_page(args.playlist)
        playlist_data = get_playlist_data(raw_data)
        for song in playlist_data:
            download(song['url'], song['title'], song['playlist_title'])
            meta_data(song, key='playlist')


if __name__ == '__main__':
    main()
