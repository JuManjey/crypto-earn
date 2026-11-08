#!/usr/bin/env bash
# Импорт keystore-файлов (созданных ethstaker-deposit-cli) в Lighthouse VC.
# Пароль keystore вводится интерактивно и не попадает в аргументы и историю shell.
# Использование: scripts/03_import_keys.sh /путь/к/validator_keys
set -euo pipefail
cd "$(dirname "$0")/.."

KEYS_DIR="${1:-}"
if [[ -z "$KEYS_DIR" || ! -d "$KEYS_DIR" ]]; then
  echo "Укажите каталог с keystore-*.json: $0 /path/to/validator_keys" >&2
  exit 1
fi
KEYS_DIR="$(cd "$KEYS_DIR" && pwd)"
shopt -s nullglob
keystores=("$KEYS_DIR"/keystore-*.json)
(( ${#keystores[@]} > 0 )) || { echo "В $KEYS_DIR нет keystore-*.json" >&2; exit 1; }

if docker ps --format '{{.Names}}' | grep -qx hoodi-lighthouse-vc; then
  echo "VC запущен. Остановите его: docker compose --profile validator stop validator" >&2
  exit 1
fi

cat <<'EOF'
ПЕРЕД ИМПОРТОМ подтвердите:
  1. Эти ключи НЕ запущены ни в одном другом validator client (ни здесь, ни на другом сервере).
     Два подписывающих экземпляра с одним ключом = риск double signing и slashing.
  2. Если ключи раньше работали в другом месте, тот VC остановлен минимум 2 эпохи назад
     и его база slashing protection импортирована (lighthouse account validator slashing-protection import).
  3. Ключи созданы для сети hoodi и с withdrawal-адресом Lido Withdrawal Vault для Hoodi
     (сверьте адрес на operatorportal.lido.fi), тип 0x01 (флаг --regular_withdrawal).
EOF
read -r -p "Все три пункта выполнены? Введите YES: " answer
[[ "$answer" == "YES" ]] || { echo "Отменено."; exit 1; }

docker compose run --rm --no-deps \
  -v "$KEYS_DIR:/keys:ro" \
  validator \
  lighthouse --network hoodi account validator import --directory /keys

echo
echo "Импорт завершён. Запуск VC (doppelganger protection включена в compose):"
echo "  docker compose --profile validator up -d validator"
echo "Первые 2-3 эпохи VC не подписывает — так задумано: он проверяет, что ключи не работают где-то ещё."
