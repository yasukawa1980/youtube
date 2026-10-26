"""IRO21 の曲順（iro/volumes/iro21.yaml の order_tracks）を bgmkit で4秒の重なりでつなぐ。中間物は ESD-02 へ（Mac の空きが少ないため）。"""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / 'bgm'))
from bgmkit import config, audio
class AudioConfig(config.Config):
    def wpath(self, *parts):
        if parts[0] == 'norm' or parts[0].startswith('music_bed'):
            return str(self.audio_work.joinpath(*parts))
        return super().wpath(*parts)
cfg = AudioConfig(config.load(str(ROOT / 'volumes/iro21.yaml')))
cfg.audio_work = Path('/Volumes/ESD-02/IRO/IRO21_素材_ドライブ2時間/_音声作業'); cfg.audio_work.mkdir(parents=True, exist_ok=True)
bed = Path(audio.build(cfg, cfg['order_tracks']))
link = Path(cfg['dir']) / '_work/music_bed.wav'
if link.is_symlink() or link.exists(): link.unlink()
link.symlink_to(bed); print('音楽の床', bed, flush=True)
