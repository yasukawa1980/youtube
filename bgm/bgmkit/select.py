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


def _local_search(files, n, feasible, score, scfg, seed=20260805):
    """交換による山登り。全探索が効かない長尺の巻で使う。

    初期解をランダムに作り、「採用1本と不採用1本を入れ替える」手を
    改善がなくなるまで繰り返す。これを restarts 回やって最良を返す。
    """
    rng = random.Random(seed)
    restarts = scfg.get("restarts", 60)
    tries = scfg.get("init_tries", 4000)
    best = None

    for _ in range(restarts):
        cur = None
        for _ in range(tries):
            c = tuple(rng.sample(files, n))
            if feasible(c):
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
            "（曲数に対して max_per_kind が小さすぎることが多い：種類数×max_per_kind ≧ count が必要）")
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
        chosen, mx, av = _local_search(files, n, feasible, score, scfg)
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


def order(cfg, chosen):
    """一致度を最小化する曲順を分枝限定で探す。"""
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
        for f in chosen:
            if f in used:
                continue
            if want and kind[f] != want:
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
