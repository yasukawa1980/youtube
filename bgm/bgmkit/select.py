"""候補から本採用を選び、曲順を決める。

旧 select_vol*.py + order_vol*.py。どちらも analysis.json だけを入力にする。

選抜の要点（Vol.9で判明）:
  一致度の最小化だけで選ぶと、音数の少ない独奏が指標上どうしても有利になり、
  10本中4本がピアノ独奏になった。max_per_kind で必ず上限を掛ける。
  最大一致度は 0.348→0.456 に悪化するが、これは払うべきコスト。

曲順の要点（Vol.9で判明）:
  隣接だけ禁じると A-B-A-B の交互並びが通り、4曲続けて2種類しか使わない箇所ができる。
  「2つ飛びも同じ種類にしない」を入れる。平均一致度はむしろ改善した。
  明るさの起伏を条件に入れてはいけない（種類を分けた設計そのものが31dBの差を生むため）。
"""
import itertools
import math
import random

from .ffutil import load_json, mmss


def _ncr(n, r):
    if r > n:
        return 0
    return math.factorial(n) // (math.factorial(r) * math.factorial(n - r))


def _alloc(kinds, avail, n, scfg, rng):
    """種ごとの採用本数を無作為に1つ決める。下限・上限・在庫を満たし、合計がちょうど n。

    下限まで先に配ってから、残りを「空いている枠」の中から無作為に選んで足す。
    枠は種ごとに (上限 − 下限) 個しか無いので、上限を超えることが構造上ありえない。
    """
    limits = scfg.get("kind_limits", {})
    max_per = scfg.get("max_per_kind", n)
    need_all = scfg.get("require_all_kinds", True)

    lo_k, hi_k = {}, {}
    for k in kinds:
        a, b = limits.get(k, (0, max_per))
        lo_k[k] = max(a, 1 if need_all else 0)
        hi_k[k] = min(b, max_per, avail[k])
        if lo_k[k] > hi_k[k]:
            return None
    if sum(lo_k.values()) > n or sum(hi_k.values()) < n:
        return None

    c = dict(lo_k)
    room = [k for k in kinds for _ in range(hi_k[k] - lo_k[k])]
    rng.shuffle(room)
    for k in room[:n - sum(lo_k.values())]:
        c[k] += 1
    return c


def _initial(by_kind, alloc, tracks, n, lo, hi, xf, rng, sweeps=400):
    """局所探索の初期解を「作る」。無作為抽選＋やり直しでは届かないため。

    ★以前は rng.sample で n 本引いて feasible を通るまで繰り返していた。これは
      在庫の構成が採用の構成に近いときしか当たらない。3時間版（153本から60本）では
      尺八が在庫の28%を占めるのに上限は17%で、無作為の60本が上限を満たす確率は
      実質ゼロ。尺の窓が狭いことも重なって、restarts をいくら増やしても
      「条件を満たす組み合わせが見つかりません」で止まっていた。

    種ごとの本数を先に決め（_alloc）、種の中だけで長短を入れ替えて尺の窓に入れる。
    種の中の交換なので、本数の条件を壊さずに合計だけを動かせる。
    """
    chosen = {k: list(rng.sample(by_kind[k], c)) for k, c in alloc.items()}
    mid = (lo + hi) / 2

    def total():
        return sum(tracks[f]["dur"] for ks in chosen.values() for f in ks) - xf * (n - 1)

    for _ in range(sweeps):
        t = total()
        if lo <= t <= hi:
            return tuple(f for ks in chosen.values() for f in ks)
        best, gap = None, abs(t - mid)
        for k, ks in chosen.items():
            rest = [f for f in by_kind[k] if f not in ks]
            for a in ks:
                for b in rest:
                    g = abs(t + tracks[b]["dur"] - tracks[a]["dur"] - mid)
                    if g < gap:
                        best, gap = (k, a, b), g
        if best is None:
            return None                      # これ以上 窓に近づけない
        k, a, b = best
        chosen[k].remove(a)
        chosen[k].append(b)
    return None


def _local_search(files, n, feasible, score, scfg, tracks, lo, hi, xf, seed=20260805):
    """交換による山登り。全探索が効かない長尺の巻で使う。

    初期解を条件どおりに組み立て、「採用1本と不採用1本を入れ替える」手を
    改善がなくなるまで繰り返す。これを restarts 回やって最良を返す。
    """
    rng = random.Random(seed)
    restarts = scfg.get("restarts", 60)
    best = None

    by_kind = {}
    for f in files:
        by_kind.setdefault(tracks[f]["kind"], []).append(f)
    kinds = sorted(by_kind)
    avail = {k: len(v) for k, v in by_kind.items()}

    for _ in range(restarts):
        cur = None
        for _ in range(scfg.get("init_tries", 20)):
            alloc = _alloc(kinds, avail, n, scfg, rng)
            if alloc is None:
                break
            c = _initial(by_kind, alloc, tracks, n, lo, hi, xf, rng)
            if c is not None and feasible(c):
                cur = c
                break
        if cur is None:
            continue
        cs = score(cur)
        improved = True
        while improved:
            improved = False
            rest = [f for f in files if f not in cur]
            rng.shuffle(rest)
            for i in range(n):
                for out in rest:
                    cand = cur[:i] + (out,) + cur[i + 1:]
                    if not feasible(cand):
                        continue
                    s = score(cand)
                    if s < cs:
                        cur, cs, improved = cand, s, True
                        break
                if improved:
                    break
        if best is None or cs < best[1]:
            best = (cur, cs)

    if best is None:
        raise SystemExit(
            "条件を満たす組み合わせが見つかりません。テイクを足すか select の条件を緩めてください。\n"
            "（曲数に対して max_per_kind が小さすぎることが多い：種類数×max_per_kind ≧ count が必要。\n"
            "  本数の条件が通っていれば、次に疑うのは total_seconds の窓が在庫の長さに対して"
            "狭すぎないか）")
    return list(best[0]), best[1][0], best[1][1]


def _sim_table(analysis):
    sim = {}
    for k, v in analysis["sim"].items():
        a, b = k.split("\t")
        sim[frozenset((a, b))] = v
    return sim


def _pairs(sim, files):
    return [sim.get(frozenset((a, b)), 0.0)
            for a, b in itertools.combinations(files, 2)]


def select(cfg):
    an = load_json(cfg.wpath("analysis.json"))
    tracks, sim = an["tracks"], _sim_table(an)
    scfg = cfg["select"]
    n = scfg["count"]
    lo, hi = scfg["total_seconds"]
    xf = cfg["audio"]["crossfade"]

    files = sorted(tracks)

    # 明示除外
    for f in cfg.get("exclude", []):
        if f in files:
            files.remove(f)

    # 種類ごとの息の量による足切り（尺八など、息が身上の楽器に使う）
    floors = scfg.get("breath_floor", {})
    cut = []
    for f in list(files):
        k = tracks[f]["kind"]
        if k in floors and tracks[f]["breath"] < floors[k]:
            cut.append((f, tracks[f]["breath"], floors[k]))
            files.remove(f)
    if cut:
        print("息の量が足りず除外（一致度だけで選ぶと純音に近い個体が勝つため先に切る）")
        for f, b, need in cut:
            print(f"  {f:36s} 息={b:.4f} < {need}")
        print()

    # 完全同一（デコード後MD5一致）は1本にまとめる
    seen = {}
    for f in list(files):
        md5 = tracks[f]["md5"]
        if md5 in seen:
            print(f"同一音源のため除外: {f}（= {seen[md5]}）")
            files.remove(f)
        else:
            seen[md5] = f

    kinds = sorted({tracks[f]["kind"] for f in files})
    limits = scfg.get("kind_limits", {})
    max_per = scfg.get("max_per_kind", n)

    def feasible(c):
        ks = [tracks[f]["kind"] for f in c]
        counts = {k: ks.count(k) for k in set(ks)}
        if scfg.get("require_all_kinds", True) and len(counts) != len(kinds):
            return False
        if max(counts.values()) > max_per:
            return False
        for k, (kmin, kmax) in limits.items():
            if not (kmin <= counts.get(k, 0) <= kmax):
                return False
        total = sum(tracks[f]["dur"] for f in c) - xf * (n - 1)
        return lo <= total <= hi

    def score(c):
        ps = _pairs(sim, c)
        return max(ps), sum(ps) / len(ps)

    def total_of(c):
        return sum(tracks[f]["dur"] for f in c) - xf * (n - 1)

    ncomb = _ncr(len(files), n)
    cap = scfg.get("exhaustive_cap", 400000)

    if ncomb <= cap:
        cand = []
        for c in itertools.combinations(files, n):
            if feasible(c):
                mx, av = score(c)
                cand.append((mx, av, total_of(c), c))
        if not cand:
            raise SystemExit(
                "条件を満たす組み合わせがありません。テイクを足すか select の条件を緩めてください。")
        cand.sort()
        print(f"条件を満たす組み合わせ: {len(cand)}通り（全探索）\n")
        print("最大  平均   尺")
        for mx, av, t, c in cand[:5]:
            print(f"{mx:.3f} {av:.3f}  {t / 60:5.1f}分")
        mx, av, t, chosen = cand[0]
    else:
        # 長尺の巻（Vol.11以降の22曲など）は全探索が効かない。
        # 30本から22本なら約585万通り×231ペアで、Pythonでは現実的な時間で終わらない。
        # ランダム初期解からの交換による山登りを多数回まわす。
        print(f"組み合わせが {ncomb:,} 通りあるため局所探索に切り替えます"
              f"（全探索の上限 {cap:,}）\n")
        chosen, mx, av = _local_search(files, n, feasible, score, scfg, tracks, lo, hi, xf)
        t = total_of(chosen)
        print(f"最良解: 最大 {mx:.3f} / 平均 {av:.3f} / {t / 60:.1f}分\n")
    print(f"\n=== 採用（最大 {mx:.3f} / 平均 {av:.3f} / {t / 60:.1f}分）===")
    for f in sorted(chosen, key=lambda x: tracks[x]["kind"]):
        d = tracks[f]
        print(f"  {d['kind']:11s} {d['dur']:6.1f}s {d['key']:>3s} 明{d['bright']:6.1f}dB  {f}")
    print("\n=== 不採用 ===")
    for f in sorted(set(files) - set(chosen), key=lambda x: tracks[x]["kind"]):
        d = tracks[f]
        print(f"  {d['kind']:11s} {d['dur']:6.1f}s  {f}")
    return list(chosen)


def _order_local_search(chosen, n, kind, key, fixed, thresh, S, ocfg):
    """長尺の巻の曲順。後戻り法でランダムな有効解を作り、2点交換で山を登る。

    分枝限定は左から埋めるため、22曲だと最後まで到達する前に予算が尽きる。
    こちらは常に完成した並びを持ったまま改善するので、曲数が増えても崩れない。
    評価は分枝限定と同じ（隣接の最大一致度 → 同点なら合計）。
    """
    no_kind_adj = ocfg.get("forbid_same_kind_adjacent", True)
    no_kind_skip1 = ocfg.get("forbid_same_kind_skip1", True)
    no_key_adj = ocfg.get("forbid_same_key_adjacent", True)
    rng = random.Random(ocfg.get("seed", 20260805))

    def placeable(o, p, f):
        if fixed.get(p + 1) and kind[f] != fixed[p + 1]:
            return False
        for d in (1, 2):
            for q in (p - d, p + d):
                if 0 <= q < n and o[q] is not None:
                    if d == 1 and no_kind_adj and kind[o[q]] == kind[f]:
                        return False
                    if d == 2 and no_kind_skip1 and kind[o[q]] == kind[f]:
                        return False
        for q in (p - 1, p + 1):
            if 0 <= q < n and o[q] is not None:
                if no_key_adj and key[o[q]] == key[f]:
                    return False
                if S(o[q], f) > thresh:
                    return False
        return True

    def valid(o):
        """完成した並びの検査。placeable を使い回すと1回ごとに O(n^2) の作り直しが
        発生して交換の山登りが実用にならないので、ここは直接 O(n) で見る。"""
        for i, f in enumerate(o):
            if fixed.get(i + 1) and kind[f] != fixed[i + 1]:
                return False
        for i in range(n - 1):
            a, b = o[i], o[i + 1]
            if no_kind_adj and kind[a] == kind[b]:
                return False
            if no_key_adj and key[a] == key[b]:
                return False
            if S(a, b) > thresh:
                return False
        if no_kind_skip1:
            for i in range(n - 2):
                if kind[o[i]] == kind[o[i + 2]]:
                    return False
        return True

    def score(o):
        adj = [S(o[i], o[i + 1]) for i in range(n - 1)]
        return (max(adj), sum(adj))

    def construct():
        """★固定枠の曲を先に置いてから残りを埋める。

        左から順に埋めると、17曲目に置くはずの⑧フル編成（1本しかない）を
        手前で使ってしまい、そこまで戻る後戻りが延々と続いて実用にならない。
        """
        o = [None] * n
        pool = list(chosen)
        for pos, kd in sorted(fixed.items()):
            cand = [f for f in pool if kind[f] == kd]
            if not cand:
                return None
            f = rng.choice(cand)
            o[pos - 1] = f
            pool.remove(f)
        rng.shuffle(pool)
        slots = [i for i in range(n) if o[i] is None]

        # ★後戻りに予算を持たせる。無いと60曲で丸一日返ってこない（3時間版で実際に23時間）。
        #   22曲までは運よく一発で埋まっていたが、曲数が増えると
        #   「最後の数枠がどうしても埋まらない」配り方に入り込む確率が上がり、
        #   そこから抜けるための後戻りが指数的に膨らむ。
        #   1回の construct を諦めても restarts が別の初期解を試すので、失うものは無い。
        budget = [ocfg.get("construct_nodes", 200000)]

        def rec(si):
            if si == len(slots):
                return True
            budget[0] -= 1
            if budget[0] <= 0:
                return False
            p = slots[si]
            cand = [f for f in pool if placeable(o, p, f)]
            rng.shuffle(cand)
            for f in cand:
                o[p] = f
                pool.remove(f)
                if rec(si + 1):
                    return True
                pool.append(f)
                o[p] = None
            return False

        return o if rec(0) else None

    best = None
    for _ in range(ocfg.get("restarts", 300)):
        o = construct()
        if o is None:
            continue
        sc = score(o)
        improved = True
        while improved:
            improved = False
            for a in range(n):
                for b in range(a + 1, n):
                    o[a], o[b] = o[b], o[a]
                    if valid(o):
                        s2 = score(o)
                        if s2 < sc:
                            sc, improved = s2, True
                            continue
                    o[a], o[b] = o[b], o[a]
        if best is None or sc < best[0]:
            best = (sc, list(o))
    if best is None:
        raise SystemExit("条件を満たす曲順がありません。制約を緩めてください。")
    (cmax, csum), seq = best
    return seq, cmax, csum


def order(cfg, chosen):
    """一致度を最小化する曲順を探す。短い巻は分枝限定、長尺は局所探索。"""
    an = load_json(cfg.wpath("analysis.json"))
    tracks, sim = an["tracks"], _sim_table(an)
    ocfg = cfg.get("order", {})
    scenes = cfg.get("scenes") or [f"場面{i + 1}" for i in range(len(chosen))]
    n = len(chosen)
    thresh = ocfg.get("adjacency_threshold", 1.0)
    fixed = {int(k): v for k, v in ocfg.get("fixed", {}).items()}   # 1始まりの場面番号 → 種類

    kind = {f: tracks[f]["kind"] for f in chosen}
    key = {f: tracks[f]["key"] for f in chosen}

    def S(a, b):
        return sim.get(frozenset((a, b)), 0.0)

    best = [None]           # (最大, 合計, 並び)
    budget = [ocfg.get("search_nodes", 3000000)]

    def dfs(seq, used, cmax, csum):
        if budget[0] <= 0:
            return
        budget[0] -= 1
        if best[0] and (cmax > best[0][0] or (cmax == best[0][0] and csum >= best[0][1])):
            return
        i = len(seq)
        if i == n:
            best[0] = (cmax, csum, list(seq))
            return
        want = fixed.get(i + 1)
        # ★後ろの固定枠のぶんは取り置く。これが無いと、17曲目に⑧フル編成を置く約束を
        #   していてもその1本を手前で使ってしまい、深さ16で必ず行き止まる。
        #   10曲の巻では偶然通っていたが、22曲では探索予算を使い切って「解なし」になる。
        avail = {}
        for g in chosen:
            if g not in used:
                avail[kind[g]] = avail.get(kind[g], 0) + 1
        need_later = {}
        for pos, kd in fixed.items():
            if pos > i + 1:
                need_later[kd] = need_later.get(kd, 0) + 1

        for f in chosen:
            if f in used:
                continue
            if want and kind[f] != want:
                continue
            if avail[kind[f]] - 1 < need_later.get(kind[f], 0):
                continue
            if i:
                p = seq[-1]
                if ocfg.get("forbid_same_kind_adjacent", True) and kind[f] == kind[p]:
                    continue
                if ocfg.get("forbid_same_key_adjacent", True) and key[f] == key[p]:
                    continue
                s = S(p, f)
                if s > thresh:
                    continue
            else:
                s = 0.0
            if (i >= 2 and ocfg.get("forbid_same_kind_skip1", True)
                    and kind[f] == kind[seq[-2]]):
                continue
            used.add(f)
            seq.append(f)
            dfs(seq, used, max(cmax, s), csum + s)
            seq.pop()
            used.discard(f)

    # ★曲数が多いと左から埋める分枝限定では 22! を覆えず、探索予算を使い切って
    #   中途半端な並びで止まる（Vol.11では最大0.348、局所探索だと0.294まで下がった）。
    #   select が組み合わせ数で全探索と局所探索を切り替えているのと同じ考え方で、
    #   長尺の巻は交換による山登りに回す。
    if n >= ocfg.get("local_search_from", 14):
        print(f"{n}曲は分枝限定では覆えないため局所探索で並べます"
              f"（切り替えの下限 {ocfg.get('local_search_from', 14)}曲）")
        seq, cmax, csum = _order_local_search(chosen, n, kind, key, fixed, thresh, S, ocfg)
    else:
        dfs([], set(), 0.0, 0.0)
        if not best[0]:
            raise SystemExit(
                f"条件を満たす曲順がありません。order.adjacency_threshold（現在 {thresh}）を"
                "上げるか、制約を緩めてください。")
        cmax, csum, seq = best[0]
    if budget[0] <= 0:
        print("※ 探索の上限に達したため、そこまでで最良の並びを採用しました"
              "（長尺の巻では最適とは限りません）。\n")
    jump = max(abs(tracks[seq[i]]["bright"] - tracks[seq[i + 1]]["bright"])
               for i in range(n - 1))
    print(f"=== 採用（隣接の最大 {cmax:.3f} / 平均 {csum / (n - 1):.3f}）===")
    print(f"    参考: 明るさの最大跳ね {jump:.1f}dB "
          "（種類を分けた設計そのものなので補正はしない）\n")
    xf = cfg["audio"]["crossfade"]
    t = 0.0
    for i, f in enumerate(seq):
        d = tracks[f]
        sc = scenes[i] if i < len(scenes) else ""
        print(f"  {i + 1:2d}. {mmss(t)}  {sc:12s} {d['kind']:9s} {d['key']:>3s} "
              f"{d['bright']:6.1f}dB  {f}")
        t += d["dur"] - (xf if i < n - 1 else 0)
    print(f"\n  合計 {t / 60:.1f}分")
    return seq
