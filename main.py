import sys
import os

from data.audioset import AudioSetMix

if __name__ == "__main__":
    path = None
    size = 1
    trim = False
    target = None
    args = sys.argv
    i = 1
    while i < len(args):
        match args[i]:
            case "-p":
                path = args[i+1]
            case "-n":
                size = int(args[i+1])
            case "-t":
                target = args[i+1]
            case _:
                print(f"Incorrect option {args[i]}")
        i += 2
    dataset = AudioSetMix(
        path=path,
        dl_size=size,
        target_dir=target,
        trim=trim
    )
