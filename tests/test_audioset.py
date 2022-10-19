import pytest

import sys
sys.path.append('/workdir/Benchmark_separation')

import pandas as pd
import os

from data.audioset import AudioSetMix

def test_init():
    mix = AudioSetMix(dl_size=1)
    samples = mix.get_samples(n_samples=3)
    assert all([sample.signal_duration < 11 for sample in samples]) or len(samples) == 0

def test_create():
    size = 5
    test = AudioSetMix(dl_size=size, target_dir="./new_dir")
    samples = test.get_samples(n_samples=size)
    assert len(samples) == pd.read_csv("./new_dir/infos.csv").shape[0]

def test_load_existing():
    ds = AudioSetMix(path="/workdir/Benchmark_separation/audioset")
    infos = pd.read_csv("/workdir/Benchmark_separation/audioset/infos.csv")
    assert (infos == ds.infos).all().all()      # Checking that the info is correct
    assert all([os.path.exists(os.path.join("/workdir/Benchmark_separation/audioset/samples", row["id"] + ".wav"))
        for _, row in infos.iterrows()])
    samples = ds.get_samples(n_samples=1000)
    assert len(samples) == infos.shape[0]
