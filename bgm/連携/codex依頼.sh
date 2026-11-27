#!/bin/bash
# Claude → Codex。依頼を投げ、返事を受け取り、申し送りに残す。
#
#   使い方: codex依頼.sh [-r] [-c] [-t 秒] "依頼文"
#     -r  読み取り専用で走らせる（調べものだけ頼むとき）
#     -c  新規セッションでなく、前回の続きとして投げる
#     -t  時間切れの秒数（既定 1800＝30分）
#     -w  リポジトリの外で書き込みを許すフォルダ（1つ。本人が許可した場所だけ）

source "$(dirname "$0")/共通.sh"

MODE=workspace-write
LIMIT=1800
RESUME=""
WRITABLE=""

while getopts "rct:w:" o; do
  case $o in
    r) MODE=read-only ;;
    c) RESUME=1 ;;
    t) LIMIT="$OPTARG" ;;
    w) WRITABLE="$OPTARG" ;;
    *) echo "使い方: $0 [-r] [-c] [-t 秒] [-w フォルダ] \"依頼文\"" >&2; exit 2 ;;
  esac
done
shift $((OPTIND-1))

REQ="${1:-}"
[ -z "$REQ" ] && { echo "依頼文がありません" >&2; exit 2; }
[ -x "$CODEX" ] || { echo "！codex が見つかりません: $CODEX" >&2; exit 3; }

lock_take "Claude→Codex" || exit 1

OUT=$(mktemp)
LOG=$(mktemp)

echo "── Codex に依頼中（${MODE}・最大 $((LIMIT/60)) 分）──────────"
echo "$REQ" | head -5
echo "────────────────────────────────────────────"

# 続きを頼むときは、前回こちらから投げた会話をIDで指定する。
# --last は「このフォルダで最後に使われた会話」を拾うので、安川さんが
# Codexアプリで開いている会話に割り込んでしまう。
STATE="$REPO/.agent-state"
mkdir -p "$STATE"

if [ -n "$RESUME" ]; then
  SID=$(cat "$STATE/codex_last_session" 2>/dev/null)
  [ -z "$SID" ] && { echo "！続きを頼める前回の会話がありません" >&2; exit 4; }
  cd "$REPO" || exit 1
  ARGS=(exec resume "$SID" --skip-git-repo-check -o "$OUT" -c "sandbox_mode=\"$MODE\"")
elif [ "$MODE" = read-only ]; then
  ARGS=(exec -C "$REPO" -s read-only --skip-git-repo-check -o "$OUT")
else
  # --approve-for-me は「書き込み可のサンドボックス＋自動審査」を含むので -s と併用できない
  ARGS=(exec -C "$REPO" --approve-for-me --skip-git-repo-check -o "$OUT")
fi

if [ -n "$WRITABLE" ] && [ "$MODE" != read-only ]; then
  [ -d "$WRITABLE" ] || { echo "！書き込み先がありません: $WRITABLE" >&2; exit 5; }
  ARGS+=(-c "sandbox_workspace_write.writable_roots=[\"$WRITABLE\"]")
  echo "書き込みを許すフォルダ: $WRITABLE"
fi

run_limited "$LIMIT" "$CODEX" "${ARGS[@]}" "$REQ" > "$LOG" 2>&1
RC=$?

NEW_SID=$(grep -m1 '^session id:' "$LOG" | awk '{print $3}')
[ -n "$NEW_SID" ] && echo "$NEW_SID" > "$STATE/codex_last_session"

REPLY=$(cat "$OUT" 2>/dev/null)

if [ -z "$REPLY" ]; then
  echo "！Codexから返事がありません（終了コード ${RC}）" >&2
  tail -25 "$LOG" >&2
  okuri_append "Claude→Codex" "依頼したが返事なし（終了コード ${RC}）" \
"**依頼：** $REQ

**結果：** 返事を受け取れなかった。ログ末尾：

\`\`\`
$(tail -15 "$LOG")
\`\`\`"
  rm -f "$OUT" "$LOG"
  exit "$RC"
fi

echo "── Codex の返事 ────────────────────────────"
echo "$REPLY"

okuri_append "Claude→Codex" "$(short_title "$REQ")" \
"**依頼（Claudeから自動送信）：**

$(quote "$REQ")

**Codexの返事：**

$(quote "$REPLY")"

echo
echo "（申し送りに記録しました）"
rm -f "$OUT" "$LOG"