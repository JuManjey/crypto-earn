#!/usr/bin/env bash
# Проверка хоста перед запуском ноды Hoodi и подготовка каталогов.
# Ничего не удаляет. Правила ufw применяются только с флагом --apply-ufw.
set -euo pipefail

cd "$(dirname "$0")/.."
APPLY_UFW=0
[[ "${1:-}" == "--apply-ufw" ]] && APPLY_UFW=1

if [[ -f .env ]]; then
  set -a
  # shellcheck source=/dev/null
  . ./.env
  set +a
fi
EL_P2P_PORT="${EL_P2P_PORT:-30303}"
CL_P2P_PORT="${CL_P2P_PORT:-9000}"
CL_QUIC_PORT="${CL_QUIC_PORT:-9001}"

FAILED=0
ok()   { printf '  [OK]   %s\n' "$*"; }
warn() { printf '  [WARN] %s\n' "$*"; }
fail() { printf '  [FAIL] %s\n' "$*"; FAILED=1; }
check() {
  local cond="$1" good="$2" bad="$3" level="${4:-fail}"
  if eval "$cond"; then ok "$good"; else "$level" "$bad"; fi
}

echo "== Система"
if [[ -r /etc/os-release ]]; then
  # shellcheck source=/dev/null
  . /etc/os-release
  ok "ОС: ${PRETTY_NAME:-unknown}"
fi
cores=$(nproc)
check "(( cores >= 4 ))" "CPU потоков: $cores" \
  "CPU потоков: $cores (минимум 4; для валидатора EIP-7870 рекомендует 8 ядер/16 потоков)"
mem_gb=$(awk '/MemTotal/ {printf "%d", $2/1024/1024}' /proc/meminfo)
check "(( mem_gb >= 31 ))" "RAM: ${mem_gb} ГБ" \
  "RAM: ${mem_gb} ГБ (нужно от 32 ГБ; для валидатора рекомендовано 64 ГБ)"

echo "== Диск под ./data"
mkdir -p data
avail_gb=$(df -BG --output=avail data | tail -1 | tr -dc '0-9')
check "(( avail_gb >= 300 ))" "Свободно: ${avail_gb} ГБ (Hoodi)" \
  "Свободно ${avail_gb} ГБ — для Hoodi закладывайте от 300 ГБ"
warn "Для mainnet нужен NVMe от 4 ТБ (EIP-7870): TLC с DRAM, не QLC и не DRAM-less."
src=$(df --output=source data | tail -1)
dev=$(lsblk -no PKNAME "$src" 2>/dev/null | head -1 || true)
rotational=1
if [[ -n "$dev" && -r "/sys/block/$dev/queue/rotational" ]]; then
  rotational=$(cat "/sys/block/$dev/queue/rotational")
fi
check "[[ $rotational == 0 ]]" "Носитель ${dev:-?} не вращающийся (SSD/NVMe)" \
  "Не удалось подтвердить SSD/NVMe для $src" warn

echo "== Время"
check "timedatectl show -p NTPSynchronized --value 2>/dev/null | grep -q yes" \
  "Системное время синхронизировано (NTP)" \
  "Время не синхронизировано: включите chrony или systemd-timesyncd"

echo "== Docker"
check "command -v docker >/dev/null" "Docker найден" \
  "Docker не установлен (https://docs.docker.com/engine/install/)"
check "docker compose version >/dev/null 2>&1" "Docker Compose v2 найден" "Docker Compose v2 не найден"

echo "== Каталоги и права"
mkdir -p data/nethermind data/lighthouse-bn data/lighthouse-vc secrets backups
chmod 700 secrets backups data/lighthouse-vc
ok "Созданы data/*, secrets/, backups/ (secrets, backups и данные VC — 700)"
check "[[ -f .env ]]" ".env найден" ".env не найден: cp .env.example .env и заполните" warn

echo "== Порты P2P для проброса на роутере/фаерволе"
echo "  EL ${EL_P2P_PORT}/tcp+udp, CL ${CL_P2P_PORT}/tcp+udp, QUIC ${CL_QUIC_PORT}/udp; RPC и API наружу не открывать"
if (( APPLY_UFW )); then
  command -v ufw >/dev/null || { fail "ufw не установлен"; exit 1; }
  sudo ufw allow OpenSSH
  sudo ufw allow "${EL_P2P_PORT}/tcp"
  sudo ufw allow "${EL_P2P_PORT}/udp"
  sudo ufw allow "${CL_P2P_PORT}/tcp"
  sudo ufw allow "${CL_P2P_PORT}/udp"
  sudo ufw allow "${CL_QUIC_PORT}/udp"
  sudo ufw default deny incoming
  sudo ufw --force enable
  ok "ufw включён; Docker-публикации на 127.0.0.1 остаются локальными"
fi

echo
if (( FAILED )); then
  echo "Есть критичные замечания — исправьте до запуска."
  exit 1
fi
echo "Хост готов. Дальше: scripts/02_gen_jwt.sh"
