#!/usr/bin/env bash
# Сравнивает версии клиентов в .env с последними релизами на GitHub.
# Код выхода 0 — всё актуально, 10 — есть обновления, 1 — ошибка.
# Только чтение: ничего не обновляет и не перезапускает.
# Без авторизации GitHub API даёт 60 запросов в час с одного IP; при ответе 403 задайте
# GITHUB_TOKEN (fine-grained токен без прав) в окружении — он передаётся curl через stdin.
set -euo pipefail
cd "$(dirname "$0")/.."
[[ -f .env ]] || { echo ".env не найден" >&2; exit 1; }
set -a
# shellcheck source=/dev/null
. ./.env
set +a

fetch() {
  if [[ -n "${GITHUB_TOKEN:-}" ]]; then
    printf 'header = "Authorization: Bearer %s"\n' "$GITHUB_TOKEN" | curl -fsSL --max-time 20 -K - "$1"
  else
    curl -fsSL --max-time 20 "$1"
  fi
}

latest() {
  local body
  body="$(fetch "https://api.github.com/repos/$1/releases/latest")" || return 1
  python3 -c 'import sys, json; print(json.load(sys.stdin)["tag_name"])' <<<"$body"
}

norm() { echo "${1#v}"; }

status=0
check() {
  local name="$1" repo="$2" current="$3" tag
  tag="$(latest "$repo")" || { echo "$name: не удалось получить релиз $repo" >&2; status=1; return; }
  if [[ "$(norm "$tag")" == "$(norm "$current")" ]]; then
    printf '%-12s %-10s актуально\n' "$name" "$current"
  else
    printf '%-12s %-10s -> доступен %s (https://github.com/%s/releases/tag/%s)\n' "$name" "$current" "$tag" "$repo" "$tag"
    (( status == 0 )) && status=10
  fi
}

check nethermind NethermindEth/nethermind "$NETHERMIND_VERSION"
check lighthouse sigp/lighthouse "$LIGHTHOUSE_VERSION"
check mev-boost flashbots/mev-boost "$MEVBOOST_VERSION"

if (( status == 10 )); then
  echo
  echo "Перед обновлением прочитайте release notes (обязательные хардфорки, миграции БД),"
  echo "затем: обновите версию в .env, docker compose pull, docker compose up -d по одному сервису."
fi
exit "$status"
