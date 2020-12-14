from __future__ import unicode_literals, print_function

import contextlib

import ffmpeg
import gevent
import gevent.monkey
from tqdm import tqdm

gevent.monkey.patch_all(thread=False)
import os
import shutil
import socket
import tempfile


class Progress:
    """
    Progress bar for ffmpeg adapted from innayatullah's fork:
    https://github.com/innayatullah/ffmpeg-python/blob/master/examples/show_progress.py
    """

    def __init__(self, video_url, path, srt_url):
        self.video_url = video_url
        self.path = path
        self.duration = float(ffmpeg.probe(video_url)['format']['duration'])
        self.srt_url = srt_url

    def run(self):
        with self.show_progress() as socket_filename:
            try:
                if not self.srt_url:
                    (
                        ffmpeg
                        .input(self.video_url)
                        .output(self.path, codec="copy")
                        .global_args('-progress', 'unix://{}'.format(socket_filename))
                        .overwrite_output()
                        .run(capture_stdout=True, capture_stderr=True)
                    )
                else:
                    (
                        ffmpeg
                        .input(self.video_url, thread_queue_size=2048)
                        .output(self.path, vcodec="copy", acodec="copy", scodec="mov_text",
                                **{'metadata:s:s:0': "language=eng", 'disposition:s:s:0': "default"})
                        .global_args('-thread_queue_size', '512', '-i', self.srt_url, '-progress',
                                     'unix://{}'.format(socket_filename))
                        .overwrite_output()
                        .run(capture_stdout=True, capture_stderr=True)
                    )
            except ffmpeg.Error as e:
                print(e.stderr)
                raise

    @contextlib.contextmanager
    def _tmpdir_scope(self):
        tmpdir = tempfile.mkdtemp()
        try:
            yield tmpdir
        finally:
            shutil.rmtree(tmpdir)

    @contextlib.contextmanager
    def _watch_progress(self, handler):
        """Context manager for creating a unix-domain socket and listen for
        ffmpeg progress events.
        The socket filename is yielded from the context manager and the
        socket is closed when the context manager is exited.
        Args:
            handler: a function to be called when progress events are
                received; receives a ``key`` argument and ``value``
                argument. (The example ``show_progress`` below uses tqdm)
        Yields:
            socket_filename: the name of the socket file.
        """
        with self._tmpdir_scope() as tmpdir:
            socket_filename = os.path.join(tmpdir, 'sock')
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            with contextlib.closing(sock):
                sock.bind(socket_filename)
                sock.listen(1)
                child = gevent.spawn(self._do_watch_progress, sock, handler)
                try:
                    yield socket_filename
                except:
                    gevent.kill(child)
                    raise

    @contextlib.contextmanager
    def show_progress(self):
        """Create a unix-domain socket to watch progress and render tqdm
        progress bar."""
        with tqdm(total=round(self.duration, 2)) as bar:
            def handler(key, value):
                if key == 'out_time_ms':
                    time = round(float(value) / 1000000., 2)
                    bar.update(time - bar.n)
                elif key == 'progress' and value == 'end':
                    bar.update(bar.total - bar.n)

            with self._watch_progress(handler) as socket_filename:
                yield socket_filename

    @staticmethod
    def _do_watch_progress(sock, handler):
        """Function to run in a separate gevent greenlet to read progress
        events from a unix-domain socket."""
        connection, client_address = sock.accept()
        data = b''
        try:
            while True:
                more_data = connection.recv(16)
                if not more_data:
                    break
                data += more_data
                lines = data.split(b'\n')
                for line in lines[:-1]:
                    line = line.decode()
                    parts = line.split('=')
                    key = parts[0] if len(parts) > 0 else None
                    value = parts[1] if len(parts) > 1 else None
                    handler(key, value)
                data = lines[-1]
        finally:
            connection.close()


if __name__ == "__main__":
    pass
