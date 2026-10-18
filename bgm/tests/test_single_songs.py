"""Run: python3 -m unittest discover -s bgm/tests -p 'test_single_songs.py' -v"""
import array
import math
import tempfile
import unittest
from pathlib import Path

from bgm.bgmkit import single_songs as app


class PlanningTests(unittest.TestCase):
    def test_times(self):
        self.assertEqual(app.seconds('12:30'), 750)
        self.assertEqual(app.seconds('01:02:03.5'), 3723.5)
        for value in ('1:60', '-1', 'nan', 'inf', True):
            with self.assertRaises(ValueError):
                app.seconds(value)

    def test_complete_short_and_exact_long(self):
        self.assertEqual(app.sequence([160], None, 1.5, 2), ([0, 0], [158.5], 318.5))
        indices, joins, duration = app.sequence([100, 80, 120], 600, 1.5)
        self.assertEqual(indices, [0, 1, 2, 0, 1, 2, 0])
        self.assertEqual(joins[:3], [98.5, 177.0, 295.5])
        self.assertEqual(duration, 600)
        with self.assertRaises(ValueError):
            app.sequence([2], 600, 1.5)


class FFmpegTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.settings = dict(lufs=-14, true_peak=-2, lra=11, preset='ultrafast', crf=26)

    def tone(self, name, frequency):
        path = self.work / name
        app.ff('-f', 'lavfi', '-i', f'sine=frequency={frequency}:sample_rate=48000:duration=12',
               '-ac', '2', '-c:a', 'pcm_f32le', path)
        return path

    def test_alternates_audio_and_crossfade(self):
        a, b = self.tone('a.wav', 440), self.tone('b.wav', 880)
        mixed = self.work / 'mixed.wav'
        app.mix_audio([a, b], [0, 1, 0], 32, 1.5, 3, mixed)
        self.assertAlmostEqual(float(app.probe(mixed)['format']['duration']), 32, places=3)
        # Confirm actual audible order A → B → A, not just a planned index list.
        for at, expected in [(5, 440), (16, 880), (26, 440)]:
            raw = self.work / 'sample.raw'
            app.ff('-ss', str(at), '-i', mixed, '-t', '0.2', '-ac', '1', '-f', 's16le', raw)
            samples = array.array('h', raw.read_bytes())
            def power(freq):
                return math.hypot(*(sum(x * fn(2 * math.pi * freq * n / 48000)
                                       for n, x in enumerate(samples))
                                    for fn in (math.sin, math.cos)))
            other = 880 if expected == 440 else 440
            self.assertGreater(power(expected), power(other) * 50)
        # Crossing point has both takes, confirming overlap rather than a hard cut.
        raw = self.work / 'overlap.raw'
        app.ff('-ss', '11.2', '-i', mixed, '-t', '0.1', '-ac', '1', '-f', 's16le', raw)
        samples = array.array('h', raw.read_bytes())
        for freq in (440, 880):
            amplitude = math.hypot(*(sum(x * fn(2 * math.pi * freq * n / 48000)
                                        for n, x in enumerate(samples))
                                     for fn in (math.sin, math.cos))) / len(samples)
            self.assertGreater(amplitude, 100)

    def test_video_loop_and_fractional_duration(self):
        tone = self.tone('tone.wav', 440)
        normalized = self.work / 'audio.m4a'
        app.normalize(tone, normalized, self.settings)
        visual = self.work / 'source.mp4'
        app.ff('-f', 'lavfi', '-i', 'color=c=blue:s=320x240:r=30:d=1',
               '-c:v', 'libx264', '-pix_fmt', 'yuv420p', visual)
        output = self.work / 'video.mp4'
        app.make_video(visual, normalized, 11.25, 3, self.settings, self.work, output)
        report = app.verify(output, 11.25, self.settings)
        self.assertEqual(report['full_decode'], 'passed')
        self.assertAlmostEqual(report['lufs'], -14, delta=1)

    def test_static_fractional_duration(self):
        tone = self.tone('tone.wav', 440)
        normalized = self.work / 'audio.m4a'
        app.normalize(tone, normalized, self.settings)
        visual = self.work / 'source.png'
        app.ff('-f', 'lavfi', '-i', 'color=c=blue:s=320x240', '-frames:v', '1', visual)
        output = self.work / 'still.mp4'
        app.make_video(visual, normalized, 11.25, 3, self.settings, self.work, output)
        self.assertEqual(app.verify(output, 11.25, self.settings)['full_decode'], 'passed')

    def test_silence_rejected(self):
        silent = self.work / 'silence.wav'
        app.ff('-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-t', '10', silent)
        with self.assertRaises(ValueError):
            app.norm_stats(silent, -14, -2, 11)

    def test_select_short_version(self):
        tone = self.tone('tone.wav', 440)
        visual = self.work / 'background.png'
        app.ff('-f', 'lavfi', '-i', 'color=c=blue:s=320x240', '-frames:v', '1', visual)
        config = self.work / 'songs.yaml'
        config.write_text(app.yaml.safe_dump({'songs': [{'id': 'test', 'name': 'test',
            'visual': visual.name, 'audio': {'path': tone.name}, 'short': {'repeats': 1}}]}))
        *_, jobs = app.prepare(config, None, ['short'])
        self.assertEqual([p['version'] for p in jobs[0][2]], ['short'])
        self.assertEqual(jobs[0][2][0]['duration'], 12)
        *_, jobs = app.prepare(config, None)
        self.assertEqual([p['version'] for p in jobs[0][2]], ['short', '10分', '30分'])


if __name__ == '__main__':
    unittest.main()
