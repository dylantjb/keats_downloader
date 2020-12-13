from gevent import monkey; monkey.patch_all()

import contextlib
import os
import shutil
import socket
import subprocess
import tempfile
from time import sleep

import ffmpeg
import gevent


class Progress:
    """
    Progress bar for ffmpeg using methods from kkroening's answer to 'Ability to track progress of an ffmpeg command':
    https://github.com/kkroening/ffmpeg-python/issues/43#issuecomment-387666560

    print_progress_bar method used from Greenstick's answer to 'Text Progress Bar in the Console':
    https://stackoverflow.com/a/34325723
    """

    def __init__(self, video_url, path, srt_url):
        self.video_url = video_url
        self.path = path
        self.duration = float(ffmpeg.probe(video_url)['format']['duration'])
        self.srt_url = srt_url
        self.previous_percentage = 0
        self.finished = False
        self.print_progress_bar(0, 100, prefix='Progress:', suffix='Complete', length=50)

    def run(self):
        with self.watch_progress(self.handler) as filename:
            if not self.srt_url:
                ffmpeg.input(self.video_url).output(self.path, codec="copy").run()
                p = subprocess.Popen(
                    (ffmpeg
                     .input(self.video_url)
                     .output(self.path, codec="copy")
                     .global_args('-progress', 'unix://{}'.format(filename))
                     .overwrite_output()
                     .compile()
                     ),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            else:
                p = subprocess.Popen(
                    (ffmpeg
                     .input(self.video_url, thread_queue_size=2048)
                     .output(self.path, vcodec="copy", acodec="copy", scodec="mov_text",
                             **{'metadata:s:s:0': "language=eng", 'disposition:s:s:0': "default"})
                     .global_args('-thread_queue_size', '512', '-i', self.srt_url, '-progress',
                                  'unix://{}'.format(filename))
                     .overwrite_output()
                     .compile()
                     ),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            out = p.communicate()

        if p.returncode != 0:
            print(out[1].decode("utf-8"))
            raise SystemExit

    @staticmethod
    def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', print_end="\r"):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
            printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """
        if iteration == total:
            # print new line on Complete
            print()
        else:
            percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
            filled_length = int(length * iteration // total)
            bar = fill * filled_length + '-' * (length - filled_length)
            print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
           

    @contextlib.contextmanager
    def _tmpdir_scope(self):
        tmpdir = tempfile.mkdtemp()
        try:
            yield tmpdir
        finally:
            shutil.rmtree(tmpdir)

    @staticmethod
    def _watch_progress(sock, handler):
        connection, client_address = sock.accept()
        data = ''
        with contextlib.closing(connection):
            while True:
                more_data = connection.recv(16).decode("utf-8")
                if not more_data:
                    break
                data += more_data
                lines = data.split('\n')
                for line in lines[:-1]:
                    parts = line.split('=')
                    key = parts[0] if len(parts) > 0 else None
                    value = parts[1] if len(parts) > 1 else None
                    handler(key, value)
                data = lines[-1]

    @contextlib.contextmanager
    def watch_progress(self, handler):
        with self._tmpdir_scope() as tmpdir:
            filename = os.path.join(tmpdir, 'sock')
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            with contextlib.closing(sock):
                sock.bind(filename)
                sock.listen(1)
                child = gevent.spawn(self._watch_progress, sock, handler)
                try:
                    yield filename
                except:
                    gevent.kill(child)
                    raise

    def handler(self, key, value):
        if key == 'out_time_ms':
            if not self.finished:
                percentage = int(int(value) / 10000. / self.duration)
                if percentage > 95:
                    self.print_progress_bar(100, 100, prefix='Progress:', suffix='Complete', length=50)
                    self.finished = True
                elif self.previous_percentage < percentage:
                    sleep(0.1)
                    self.print_progress_bar(percentage, 100, prefix='Progress:', suffix='Complete', length=50)


if __name__ == "__main__":
    pass
