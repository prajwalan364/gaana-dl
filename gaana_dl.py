import argparse
from utils.parser import parse_page
from utils.gaana import get_song_data, get_albumb_data, download, meta_data


def main():
    arg_parser = argparse.ArgumentParser(description="Gaana Music Downloader")
    arg_parser.add_argument("-s", dest="song", help="Enter the song url")
    arg_parser.add_argument("-a", dest="album", help="Enter albun url")
    args = arg_parser.parse_args()

    if not (args.song or args.album):
        arg_parser.error("No Action Requested..!,  add -h for help")

    if args.song:
        if "gaana.com" not in args.song:
            arg_parser.error("Wrong Url")
        raw_data = parse_page(args.song)
        song_data = get_song_data(raw_data)
        download(song_data['url'], song_data['title'], song_data['album'])
        meta_data(song_data)

    if args.album:
        if "gaana.com" not in args.album:
            arg_parser.error("Wrong Url")
        raw_data = parse_page(args.album)
        album_data = get_albumb_data(raw_data)
        for song in album_data['tracks']:
            download(song['url'], song['title'], song['album'])
            meta_data(song)


if __name__ == '__main__':
    main()
