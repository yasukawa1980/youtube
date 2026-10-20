"""Subtitle page layout shared by the renderer and the SRT-only rebuild.

A page is at most two lines. English splits a sentence into evenly sized pages
and balanced lines, so no page is left holding a single word for a split second.
"""
import math
import re

EN_LINE = 42
# Names kept on one subtitle line.
NOBREAK = ["Nina de Garis Davies", "The Metropolitan Museum of Art", "Book of Going Forth by Day",
           "Book of the Dead", "Amenemhat I"]


def wrap_ja(t, n=22):
    """Preserve Claude v02's punctuation/particle boundary logic."""
    lines = []
    while len(t) > n:
        k = -(-len(t)//n)
        target = round(len(t)/k)
        def score(i):
            if t[i-1] == "、":
                return abs(i-target)
            if t[i-1] in "はがをにでともへや" and not "ぁ" <= t[i] <= "ゖ":
                return abs(i-target)+3
            if t[i-1] == "の" and not "ぁ" <= t[i] <= "ゖ":
                return abs(i-target)+6
            return None
        cands = [(score(i), i) for i in range(4, min(n, len(t)-2)+1) if score(i) is not None]
        cut = min(cands)[1] if cands else n
        if cut < len(t) and t[cut] in "、。！？）」』":
            cut += 1
        lines.append(t[:cut])
        t = t[cut:]
    if t:
        lines.append(t)
    return lines


WEAK = {"a", "an", "the", "of", "on", "to", "in", "and", "or", "with", "for", "by",
        "at", "from", "as", "is", "was", "were", "that", "his", "her", "its", "their", "de"}


def _split_words(words, parts, limit, punct=12):
    """Split words into `parts` runs of similar length, each within `limit` chars.

    Breaks after , ; : are preferred by `punct`; never end a run on an article,
    preposition or similar small word if avoidable. Returns None when no split fits.
    """
    n = len(words)
    total = len(" ".join(words))
    best = {0: (0.0, [])}
    for k in range(1, parts+1):
        nxt = {}
        for i, (cost, cuts) in best.items():
            for j in range(i+1, n+1):
                if (k == parts) != (j == n):
                    continue
                run = " ".join(words[i:j])
                if len(run) > limit:
                    break
                c = cost+(len(run)-total/parts)**2
                if j < n and not re.search(r"[,;:.?!]$", words[j-1]):
                    c += punct
                if j < n and words[j-1].lower() in WEAK:
                    c += max(4*punct, 300)
                if j not in nxt or c < nxt[j][0]:
                    nxt[j] = (c, cuts+[j])
        best = nxt
    if n not in best:
        return None
    cuts = [0]+best[n][1]
    return [" ".join(words[a:b]) for a, b in zip(cuts, cuts[1:])]


def pages_en(text, line=EN_LINE):
    for name in NOBREAK:
        text = text.replace(name, name.replace(" ", "\u00a0"))
    words = text.split(" ")
    pages = max(1, math.ceil(len(text)/(2*line)))
    while True:
        runs = _split_words(words, pages, 2*line+1, punct=150)
        if runs:
            out = []
            for run in runs:
                rows = [run] if len(run) <= line else _split_words(run.split(" "), 2, line)
                if rows is None:
                    break
                out.append("\n".join(rows).replace("\u00a0", " "))
            else:
                return out
        pages += 1


def pages(text, lang):
    if lang == "en":
        return pages_en(text)
    rows = wrap_ja(text)
    return ["\n".join(rows[k:k+2]) for k in range(0, len(rows), 2)]


def sentence_cues(cue, lang):
    """Divide one measured sentence span among its pages by character share."""
    chunks = pages(cue["text"], lang)
    weights = [len(x.replace("\n", "")) for x in chunks]
    total, start, out = sum(weights), cue["start"], []
    for k, (chunk, weight) in enumerate(zip(chunks, weights)):
        end = cue["end"] if k == len(chunks)-1 else start+(cue["end"]-cue["start"])*weight/total
        out.append({"sentence_id": cue["id"], "text": chunk, "start": start, "end": end})
        start = end
    return out


def stamp(t):
    ms = round(t*1000)
    return f"{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}"


def to_srt(cues):
    return "\n\n".join(f'{i}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["text"]}'
                       for i, c in enumerate(cues, 1))+"\n"
