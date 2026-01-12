#!/bin/bash
# Sync individual data sources
#
# Usage:
#   ./scripts/sync-source.sh daily-silk
#   ./scripts/sync-source.sh ai-news
#   ./scripts/sync-source.sh github
#   ./scripts/sync-source.sh docs
#   ./scripts/sync-source.sh all

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$REPO_ROOT"

sync_daily_silk() {
    echo "Syncing daily-silk..."
    rm -rf temp-daily-silk
    git clone --depth 1 https://github.com/madjin/daily-silk.git temp-daily-silk
    mkdir -p daily-silk
    find temp-daily-silk/data -name "*.md" | tar -cf - -T - | tar -xf - --strip-components=2 -C daily-silk/
    rm -rf temp-daily-silk
    echo "Done: daily-silk"
}

sync_ai_news() {
    echo "Syncing ai-news..."
    rm -rf temp-ai-news
    git clone --depth 1 --branch gh-pages https://github.com/M3-org/ai-news.git temp-ai-news
    mkdir -p ai-news/elizaos ai-news/hyperfy
    rsync -av --delete temp-ai-news/elizaos/json/ ai-news/elizaos/json/
    rsync -av --delete temp-ai-news/elizaos/md/ ai-news/elizaos/md/
    rsync -av --delete temp-ai-news/elizaos/discord/ ai-news/elizaos/discord/
    [ -d temp-ai-news/hyperfy ] && rsync -av --delete temp-ai-news/hyperfy/ ai-news/hyperfy/
    rm -rf temp-ai-news
    echo "Done: ai-news"
}

sync_github() {
    echo "Syncing github..."
    rm -rf temp-github
    git clone --depth 1 --branch _data https://github.com/elizaOS/elizaos.github.io.git temp-github
    mkdir -p github/summaries github/api github/contributors
    rsync -av --delete temp-github/data/elizaos_eliza/ github/ --exclude='summaries' --exclude='api' --exclude='contributors'
    rsync -av --delete temp-github/data/summaries/ github/summaries/
    rsync -av --delete temp-github/data/api/ github/api/
    rsync -av --delete temp-github/data/contributors/ github/contributors/
    rm -rf temp-github
    echo "Done: github"
}

sync_docs() {
    echo "Syncing docs..."
    rm -rf temp-docs
    git clone --depth 1 --branch develop https://github.com/elizaOS/eliza.git temp-docs
    mkdir -p docs
    rsync -av --delete temp-docs/docs/ docs/
    rm -rf temp-docs
    echo "Done: docs"
}

case "${1:-}" in
    daily-silk)
        sync_daily_silk
        ;;
    ai-news)
        sync_ai_news
        ;;
    github)
        sync_github
        ;;
    docs)
        sync_docs
        ;;
    all)
        sync_daily_silk
        sync_ai_news
        sync_github
        sync_docs
        ;;
    *)
        echo "Usage: $0 {daily-silk|ai-news|github|docs|all}"
        exit 1
        ;;
esac
