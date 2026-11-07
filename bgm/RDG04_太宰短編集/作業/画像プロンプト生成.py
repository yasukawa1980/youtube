"""RDG04の絵のプロンプト全文を書き出す（コピー用md と 場面ごとのtxt）。生成は本人かCodex。"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE.parent / '画像プロンプト'
MD = HERE.parent.parent / 'RDG04_コピー用プロンプト.md'

NOBODY = 'No people, no figures, no silhouettes of people, no faces, no hands, no animals except those named above, no cats.'
STYLE = ('Japanese shin-hanga woodblock print in the manner of the 1920s-30s revival: flat layered areas of colour, '
         'visible woodgrain in the flat passages, softly gradated sky (bokashi), Western perspective and cast light held '
         'inside Japanese printmaking. Everything in the scene is drawn as part of the print, in the same flat woodblock '
         'manner, never photographic. Calm, dreamlike and hushed. Strong clear difference between the light and dark masses '
         'so the image still reads when reduced to a thumbnail. No text, no signature, no seal stamp, no lettering of any '
         'kind. No modern objects: no power lines, no cars, no trucks, no plastic, no electric signs. Wide 16:9 landscape. Exposed so that '
         'texture is clearly visible everywhere. Shadows are lifted and open, full of visible detail, nothing crushed to '
         'pure black. High dynamic range, rich texture even in the darkest areas.')

SCENES = [
 ('01', '夜のシラクスの町', '走れメロス 0:00〜11:30',
  'An ancient walled hill city of the Mediterranean, like old Syracuse in Sicily, at night after sunset. Narrow stone streets climb between pale limestone houses with flat roofs and small arched doorways; every window is dark and shuttered, and the streets are silent and empty. On the hilltop stands a stern royal castle of heavy stone with a few small torches burning on its walls, the warmest spots in the image. Above, a deep indigo sky with a thin new moon and quiet stars. Colours: deep indigo, pale grey limestone, small orange torchlight. Lonely and hushed, a little uneasy.'),
 ('02', '雨の村と羊の野', '走れメロス 11:30〜18:17',
  'A small farming village of ancient Sicily on a dim rainy morning, drawn as a soft blue-grey dawn scene and not as a bright day. Low stone farmhouses with tiled roofs, a simple stone sheepfold with a few white sheep huddled under its roof, an olive tree, and a wide meadow running to low hills. Thin slanting lines of rain fill the air in the woodblock manner, and pools on the path reflect the grey sky. One farmhouse window glows warm yellow as if a small celebration is going on inside. Colours: blue-grey, soft green meadow, white sheep, one warm window.'),
 ('03', '濁流の川', '走れメロス 18:17〜31:05',
  'A wide river in flood among wooded hills under a heavy dark rain sky. The muddy torrent surges in great curling waves drawn in the bold stylised manner of Japanese woodblock prints, carrying broken branches. The remains of a wooden bridge are gone; only two broken stumps of piers stand in the water. On the far bank a narrow mountain road climbs up into dark pines toward a pass. Rain falls in fine slanting lines. Colours: dark slate blue, ochre-brown water with pale foam, black-green pines. Powerful but still drawn calmly, nothing gory.'),
 ('04', '斜陽の森と遠い町', '走れメロス 31:05〜43:03',
  'Late afternoon toward sunset after the rain, drawn as an evening scene. In the foreground a small clear spring trickles out of a cleft in a mossy rock beside a forest road, glinting. Beyond the trees the road runs downhill across fields toward a far walled city on a hill, its towers small and dark against the sky. The setting sun throws long low red-gold light through the leaves so that they glow as if on fire, and the sky above is deep crimson fading to violet. Colours: crimson and gold light, violet sky, dark green-black forest, a small bright spring.'),
 ('05', '夏の明け方の小川', '満願 43:03〜49:00',
  'A quiet small town in Izu, Japan, in the 1930s, at early summer dawn, drawn as a blue-hour scene and not as a bright day. Seen from the wooden veranda of an old Japanese house: beyond a low hedge, a green meadow of tall summer grass and a clear little stream running full and slow, with a narrow earth path along it. The path is empty. Morning mist lies low over the water, and a pale lemon-pink light rises behind distant hills. Colours: soft blue-green, pale mist, lemon-pink sky, dark wood veranda. Fresh, calm and quietly happy.'),
 ('06', '夕暮れの遠浅の海', '黄金風景 49:00〜1:00:51',
  'A wide shallow tidal beach on Tokyo Bay near Funabashi in the 1930s, at golden evening, drawn as an evening scene. Long flat wet sand and shallow water stretch far out, reflecting the low sun so the whole surface shines like beaten gold. A few small wooden stakes of seaweed farms stand in the shallows. On the left a small old wooden house with a pink oleander bush in bloom. The sky is amber and soft rose, darkening to blue at the top. Colours: gold, amber, rose, dark blue-grey shore. Peaceful and a little wistful.'),
 ('07', '雪の夜道', '雪の夜の話 1:00:51〜1:08:35',
  'A quiet residential lane near Kichijoji, Tokyo, in the 1940s, on a snowy night. Deep fresh snow covers the narrow road and the low wooden fences; the trees on both sides bow under heavy snow. Snowflakes fall thickly and softly through the light of a single old street lamp, swirling like countless fireflies. A small red post box stands capped with snow. A row of footprints runs along the road. Colours: deep blue night, soft white snow, warm yellow lamplight, one small red post box.'),
 ('08', '雪の夜の窓あかり', '雪の夜の話 1:08:35〜末尾',
  'A small old wooden Japanese house at night in deep snow, seen from the garden. Its sliding glass doors glow with warm yellow light from inside, falling in soft rectangles across the snow. Snow is gently falling, the trees and the roof are heavy with white, and the night sky is deep indigo. Inside, only a low table and a lamp are suggested through the glass, no one visible. Colours: deep indigo, soft white snow, warm golden window light. Tender, warm and very calm.'),
 ('09', 'サムネ専用（本編には使わない）', 'サムネ',
  'Composed for a thumbnail. The left third of the image is a calm, dark, simple area of deep violet evening sky with almost no detail, so lettering can be placed over it. In the right two thirds, a long road runs straight toward an ancient walled hill city of the Mediterranean, its towers dark against an enormous setting sun that is a clean round disc of deep red-orange, the brightest and warmest shape in the image. Long red light lies across the road and the fields. Strong contrast, so it still reads at the size of a postage stamp. Colours: deep violet, red-orange sun, dark silhouetted city, golden road.'),
]


def full(body):
    return f'{body} {NOBODY} {STYLE}'


def main():
    OUT_DIR.mkdir(exist_ok=True)
    out = ['# RDG04 コピー用プロンプト — 太宰治 短編集（新版画・8場面＋サムネ）', '',
           '生成は本人かCodex。各ブロックを**そのまま全文**貼る（画風と露出の文まで含む）。16:9・横長。',
           '置き場：`bgm/RDG04_太宰短編集/画像/rdg04_NN.png`（NN＝下の番号。サムネは rdg04_09.png）。',
           '全場面に人物を描かない。受け取ったら明るさの並びと潰れを測る。', '']
    for n, name, where, body in SCENES:
        text = full(body)
        (OUT_DIR / f'{n}_{name}.txt').write_text(text + '\n')
        out += [f'## {n}_{name}（{where}）', '', '```', text, '```', '']
    MD.write_text('\n'.join(out))
    print(len(SCENES), max(len(full(s[3])) for s in SCENES))


if __name__ == '__main__':
    main()
