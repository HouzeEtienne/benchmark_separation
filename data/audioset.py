
# import sys
# sys.path.append('/workdir/Benchmark_separation')

from data.mix_data import MixDataset
import youtube_dl
# import nussl
import os
import pandas as pd
from progress.bar import Bar
import requests
import scipy.io.wavfile as wavfile

YDL_OPTS = {
    "format": "bestaudio/best",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "wav"
    }],
    "outtmpl": "./audioset/samples/%(id)s.%(ext)s"
}
URL_AUDIOSET = "http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/unbalanced_train_segments.csv"
YOUTUBE_BASE = "https://youtube.com/watch?v="

class AudioSetMix(MixDataset):
    def __init__(self, path: str | None=None, dl_size: int|None=None, target_dir: str|None=None,
        trim=False) -> None:
        """Builds an MixDataset object to generate samples from the audioset DS.

        The audioset DS is available at `https://research.google.com/audioset/download.html`

        Args:
            path (str | None, optional): path to either the csv file containing the addresses of the folder containing the dataset. Defaults to None.
        """        
        super().__init__()
        self.infos: pd.DataFrame = None
        self.path = path
        self.ydl_options = YDL_OPTS
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
            self.infos = pd.read_csv(self.path)
            if dl_size is not None:
                self.infos = self.infos.sample(dl_size)
            self.path = os.path.dirname(self.path)
            with youtube_dl.YoutubeDL(YDL_OPTS) as ydl:
                for idx, row in self.infos.iterrows():
                    print(idx, row)
                    with Bar("Downloading audio samples", max=dl_size) as bar:
                        try:
                            if not os.path.exists(os.path.join(self.path, f"{row['id']}.wav")):
                                ydl.download([YOUTUBE_BASE + row["id"]])
                            if trim:
                                print(f"Now trimming video")
                                self._trim_sound(row)
                        except youtube_dl.utils.ExtractorError as exc:
                            print(f"Could not download {row['id']}")
                            self.infos = self.infos.drop(labels=[idx])
                        except youtube_dl.utils.DownloadError as exc:
                            print(f"Could not download {row['id']}")
                            self.infos = self.infos.drop(labels=[idx])
                        except KeyboardInterrupt:
                            self.infos = self.infos.drop(labels=[idx])
                            break
                        bar.next()
            print(os.path.join(self.path, "infos.csv"))
            print(self.infos.shape)
            self.infos.to_csv(os.path.join(self.path, "infos.csv"))
        elif os.path.isdir(self.path):
            self.infos = pd.read_csv(os.path.join(self.path, "infos.csv"))
            print(f"Dataset exists, loading from it, size of {self.infos.shape}")
        else:
            print("Problem: a path was given, but does not correspond to a directory or a csv file")
            print(self.path)
            raise ValueError()

    def _trim_sound(self, info_row: pd.Series):
        filepath = os.path.join(self.path, "samples", info_row["id"] + ".wav")
        sr, y = wavfile.read(filepath)
        print(y.shape)
        start, stop = int((float(info_row["start"])) * sr), int(float(info_row["stop"]) * sr)
        wavfile.write(filename=filepath, rate=sr, data=y[start:stop])

    def _download_clean_csv(self, csv_url: str, target_path: str):
        """Small helper method

        Args:
            csv_url (str): path to the csv describing the audioset DS
            target_path (str): path to write the clean csv to.
        """        
        print("No path given, downloading the set infos")
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
            

    # def get_samples(self, n_samples=1) -> list[nussl.AudioSignal]:
    #     to_ret = []
    #     counter = 0
    #     for _, row in self.infos.iterrows():
    #         to_ret.append(nussl.AudioSignal(os.path.join(self.path, "samples", f"{row['id']}.wav")))
    #         counter += 1
    #         if counter > n_samples:
    #             break
    #     return to_ret