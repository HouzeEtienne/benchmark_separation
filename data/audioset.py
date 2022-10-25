
# import sys
# sys.path.append('/workdir/Benchmark_separation')

import yt_dlp
import os
import pandas as pd
from progress.bar import Bar
import requests
import scipy.io.wavfile as wavfile
import math
# if os.environ.get("NUSSL", False):
#     import nussl

YDL_OPTS = {
    "format": "bestaudio/best",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "wav"
    }],
    "outtmpl": "./audioset/samples/%(id)s.%(ext)s",
    "quiet": True
}
URL_AUDIOSET = "http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/unbalanced_train_segments.csv"
YOUTUBE_BASE = "https://youtube.com/watch?v="

class AudioSetDownloader:
    def __init__(self) -> None:
        super().__init__()
    
    def download( self,
            dl_size: int|None=None,
            target_dir: str|None=None,
            trim=False, verbose=False,
            sep="comma",
            start_idx: int=0) -> None:
        """Downloads the datset, fetching it from the online website
        The audioset DS is available at `https://research.google.com/audioset/download.html`

        Args:
            dl_size (int | None, optional): _description_. Defaults to None.
            target_dir (str | None, optional): _description_. Defaults to None.
            trim (bool, optional): _description_. Defaults to False.
            verbose (bool, optional): _description_. Defaults to False.
            sep (str, optional): separator to use to read the csv file. Defaults to "comma", to read standard csv files.
            start_idx (int, optional): it is possible to specify an index to start with, so that 
        """
        super().__init__()
        self.infos: pd.DataFrame = None
        self.path = None
        self.ydl_options = YDL_OPTS
        self.is_trimmed = trim
        self.start_idx = start_idx
        if verbose: 
            self.ydl_options["quiet"] = False
        if self.path is None:
            if target_dir is not None:
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)
                filepath = os.path.join(target_dir, "infos.csv")
                self.ydl_options["outtmpl"] = target_dir + "/samples/%(id)s.%(ext)s"
            else:
                filepath = "./audioset/infos.csv"
            self._download_clean_csv(URL_AUDIOSET, filepath)
            self.path = filepath
            print(self.path)
        if os.path.exists(self.path) and self.path[-4:] == ".csv":
            print("Using csv file to download samples.")
            if sep == "tab":
                self.infos = pd.read_csv(self.path, sep="\t")
            else:
                self.infos = pd.read_csv(self.path)
            if dl_size is None:
                dl_size = math.inf
            self.path = os.path.dirname(self.path)
            new_infos = pd.DataFrame({col: [] for col in self.infos.columns})
            self.infos = self.infos.loc[self.start_idx:]
            counter_downloads = 0
            with yt_dlp.YoutubeDL(self.ydl_options) as ydl:
                with Bar("Downloading audio samples", max=dl_size) as bar:
                    for idx, row in self.infos.iterrows():
                        if counter_downloads >= dl_size:
                            break
                        try:
                            if not os.path.exists(os.path.join(self.path, f"{row['id']}.wav")):
                                ydl.download([YOUTUBE_BASE + row["id"]])
                            if trim:
                                self._trim_sound(row, idx)
                            else:
                                os.move()
                            new_infos.loc[idx] = row
                            counter_downloads += 1
                        except yt_dlp.utils.ExtractorError as exc:
                            # self.infos = self.infos.drop(labels=[idx])
                            pass
                        except yt_dlp.utils.DownloadError as exc:
                            # self.infos = self.infos.drop(labels=[idx])
                            pass
                        except KeyboardInterrupt:
                            # self.infos = self.infos.drop(labels=[idx])
                            print("Stopping with user interrupt")
                            break
                        bar.next()
            self.infos = new_infos
            self.infos.to_csv(os.path.join(self.path, "infos.csv"))
        elif os.path.isdir(self.path):
            self.infos = pd.read_csv(os.path.join(self.path, "infos.csv"))
            print(f"Dataset exists, loading from it, size of {self.infos.shape}")
        else:
            print("Problem: a path was given, but does not correspond to a directory or a csv file")
            print(self.path)
            raise ValueError()

    def _trim_sound(self, info_row: pd.Series, index: int|None = None):
        """Helper method to trim sounds that have been downloaded, to keep only the annotated part

        Args:
            info_row (pd.Series): the row from the `infos.csv` file describing the sound to trim
            index (int | None, optional): Index of the row, used to name the new file, if provided. Defaults to None (no renaming).
        """        
        filepath = os.path.join(self.path, "samples", info_row["id"] + ".wav")
        if index is None:
            new_fp = filepath
        else:
            new_fp = os.path.join(self.path, 'samples', str(index) + ".wav")
        sr, y = wavfile.read(filepath)
        start, stop = int((float(info_row["start"])) * sr), int(float(info_row["stop"]) * sr)
        wavfile.write(filename=new_fp, rate=sr, data=y[start:stop])
        os.remove(filepath)

    def _download_clean_csv(self, csv_url: str, target_path: str):
        """Small helper method to download the csv and clean it so it can be easily parsed by Pandas.

        Args:
            csv_url (str): path to the csv describing the audioset DS
            target_path (str): path to write the clean csv to.
        """        
        try:
            with open(target_path, "wb+") as info:
                info.write(requests.get(csv_url).content)
            lines = []
            with open(target_path, "r") as info:
                lines = info.readlines()
            with open(target_path, "w") as info:
                info.write("id,start,stop,tags\n")
                for line in lines:
                    if len(line) >= 4:
                        if line[0] != "#":
                            info.write(line.replace(",/", " "))
            self.path = target_path
        except Exception as exc:
            print("Trouble getting the csv file, maybe check if the URL is correct or download manually")
