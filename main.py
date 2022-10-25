import argparse

from data.audioset import AudioSetDownloader

if __name__ == "__main__":
    start = 0
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", help="Some path [DEPRECATED]", default=None)
    parser.add_argument("-n", "--number", help="Maximum number of files to download", default=1, type=int)
    parser.add_argument("-t", "--target", help="Target directory to store the dataset to", default=None)
    parser.add_argument("--trim", action='store_true', help="Whether to trim the output or not, defaults to False", default=False)
    parser.add_argument("-v", "--verbose", help="Increase verbosity", action="store_true", default=False)
    parser.add_argument("-s", "--start", help="Start index, useful to resume downloading", type=int, default=0)
    args = parser.parse_args()
    print(args)
    target = args.target
    size = args.number
    trim = args.trim
    verbose = args.verbose
    start = args.start
    downloader = AudioSetDownloader()
    downloader.download(
        dl_size=size,
        target_dir=target,
        trim=trim,
        verbose=verbose,
        start_idx=start
    )
