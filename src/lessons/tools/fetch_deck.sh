#!/bin/bash
# 시험 카드(SRS 덱 FULLDECK)를 BAEggman/qoaq에서 받아 src/lessons/.cache/deck.json으로
set -e
HERE="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$HERE/.cache"
TMP="$(mktemp -d)"
git clone -q --depth 1 https://github.com/BAEggman/qoaq.git "$TMP/qoaq"
node "$HERE/tools/parse_deck.js" "$TMP/qoaq/한의학_인출훈련_학습과학.html" "$HERE/.cache/deck.json"
