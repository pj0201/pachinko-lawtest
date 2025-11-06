#!/bin/bash

# RAG Bulk Problem Generator - Quick Start Script
#
# 使用方法:
#   ./generate-problems.sh [provider]  [output_path]
#
# プロバイダー: groq (推奨), ollama, claude, openai, mistral
# 例:
#   ./generate-problems.sh groq
#   ./generate-problems.sh ollama ./data/problems_custom.json
#

set -e

# カラー出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# デフォルト値
LLM_PROVIDER="${1:-groq}"
OUTPUT_PATH="${2:-./data/generated_problems.json}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  🎰 RAG Bulk Problem Generator${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 1. 事前チェック
echo -e "${YELLOW}📋 Pre-flight Checks${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ディレクトリ確認
if [ ! -d "$PROJECT_ROOT/backend" ]; then
  echo -e "${RED}✗ backend ディレクトリが見つかりません${NC}"
  exit 1
fi
echo -e "${GREEN}✓ backend ディレクトリ: $PROJECT_ROOT/backend${NC}"

# OCR データ確認
OCR_FILE="$PROJECT_ROOT/data/ocr_results_corrected.json"
if [ ! -f "$OCR_FILE" ]; then
  echo -e "${RED}✗ OCR データが見つかりません: $OCR_FILE${NC}"
  exit 1
fi
OCR_SIZE=$(du -h "$OCR_FILE" | cut -f1)
echo -e "${GREEN}✓ OCR データ: $OCR_FILE ($OCR_SIZE)${NC}"

# Node.js 確認
if ! command -v node &> /dev/null; then
  echo -e "${RED}✗ Node.js がインストールされていません${NC}"
  exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js: $NODE_VERSION${NC}"

echo ""

# 2. LLM プロバイダー検証
echo -e "${YELLOW}🤖 LLM Provider Setup${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

case "$LLM_PROVIDER" in
  groq)
    if [ -z "$GROQ_API_KEY" ]; then
      echo -e "${YELLOW}⚠️  GROQ_API_KEY が設定されていません${NC}"
      echo "   → https://console.groq.com/keys から API キーを取得してください"
      echo "   → 設定: export GROQ_API_KEY=gsk_..."
      exit 1
    fi
    echo -e "${GREEN}✓ Groq API キー: 設定済み${NC}"
    echo -e "${GREEN}  ℹ️  期待実行時間: 15-25 分${NC}"
    ;;

  ollama)
    if ! command -v ollama &> /dev/null; then
      echo -e "${YELLOW}⚠️  Ollama がインストールされていません${NC}"
      echo "   → https://ollama.ai から Ollama をインストールしてください"
      echo "   → 起動: ollama serve (別ターミナルで)"
      exit 1
    fi
    echo -e "${GREEN}✓ Ollama: インストール済み${NC}"
    echo -e "${GREEN}  ℹ️  期待実行時間: 30-45 分（ローカル依存）${NC}"
    ;;

  claude)
    if [ -z "$CLAUDE_API_KEY" ]; then
      echo -e "${YELLOW}⚠️  CLAUDE_API_KEY が設定されていません${NC}"
      echo "   → https://console.anthropic.com から API キーを取得してください"
      echo "   → 設定: export CLAUDE_API_KEY=sk-ant-..."
      exit 1
    fi
    echo -e "${GREEN}✓ Claude API キー: 設定済み${NC}"
    echo -e "${GREEN}  ℹ️  期待実行時間: 20-30 分${NC}"
    ;;

  openai)
    if [ -z "$OPENAI_API_KEY" ]; then
      echo -e "${YELLOW}⚠️  OPENAI_API_KEY が設定されていません${NC}"
      echo "   → https://platform.openai.com/api-keys から API キーを取得してください"
      echo "   → 設定: export OPENAI_API_KEY=sk-..."
      exit 1
    fi
    echo -e "${GREEN}✓ OpenAI API キー: 設定済み${NC}"
    ;;

  mistral)
    if [ -z "$MISTRAL_API_KEY" ]; then
      echo -e "${YELLOW}⚠️  MISTRAL_API_KEY が設定されていません${NC}"
      echo "   → https://console.mistral.ai から API キーを取得してください"
      echo "   → 設定: export MISTRAL_API_KEY=..."
      exit 1
    fi
    echo -e "${GREEN}✓ Mistral API キー: 設定済み${NC}"
    ;;

  *)
    echo -e "${RED}✗ 不明な LLM プロバイダー: $LLM_PROVIDER${NC}"
    echo "   対応プロバイダー: groq, ollama, claude, openai, mistral"
    exit 1
    ;;
esac

echo ""

# 3. 出力ディレクトリ作成
OUTPUT_DIR=$(dirname "$OUTPUT_PATH")
if [ ! -d "$OUTPUT_DIR" ]; then
  mkdir -p "$OUTPUT_DIR"
  echo -e "${GREEN}✓ 出力ディレクトリ作成: $OUTPUT_DIR${NC}"
else
  echo -e "${GREEN}✓ 出力ディレクトリ: $OUTPUT_DIR${NC}"
fi

echo ""

# 4. メモリ確認
AVAILABLE_MEMORY=$(free -g | awk '/^Mem:/{print $7}')
if [ "$AVAILABLE_MEMORY" -lt 2 ]; then
  echo -e "${YELLOW}⚠️  メモリが少なくなっています（利用可能: ${AVAILABLE_MEMORY}GB）${NC}"
  echo "   → メモリ不足が発生する場合は Node.js のメモリ制限を増加してください"
fi

echo ""
echo -e "${YELLOW}🚀 Generation Starting${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 5. 生成実行
cd "$PROJECT_ROOT"

export LLM_PROVIDER="$LLM_PROVIDER"

# メモリが少ない場合はメモリ制限を設定
if [ "$AVAILABLE_MEMORY" -lt 2 ]; then
  echo -e "${YELLOW}ℹ️  メモリ制限を設定して実行します（4GB）${NC}"
  node --max-old-space-size=4096 backend/generate-bulk-problems.js --output "$OUTPUT_PATH"
else
  node backend/generate-bulk-problems.js --output "$OUTPUT_PATH"
fi

GENERATION_EXIT_CODE=$?

echo ""

# 6. 完了処理
if [ $GENERATION_EXIT_CODE -eq 0 ]; then
  echo -e "${GREEN}✅ Generation Complete!${NC}"

  # 結果ファイル情報
  if [ -f "$OUTPUT_PATH" ]; then
    FILE_SIZE=$(du -h "$OUTPUT_PATH" | cut -f1)
    PROBLEM_COUNT=$(cat "$OUTPUT_PATH" | grep -o '"id"' | wc -l)

    echo ""
    echo -e "${BLUE}📊 Results:${NC}"
    echo "  File: $OUTPUT_PATH"
    echo "  Size: $FILE_SIZE"
    echo "  Problems: ~$PROBLEM_COUNT (from JSON)"

    echo ""
    echo -e "${BLUE}📝 Next Steps:${NC}"
    echo "  1. Review: cat $OUTPUT_PATH | jq '.metadata'"
    echo "  2. Test: Start the React app and load the problems"
    echo "  3. Deploy: Copy to production environment"
  fi

  echo ""
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

else
  echo -e "${RED}❌ Generation Failed!${NC}"
  echo "   Exit Code: $GENERATION_EXIT_CODE"
  echo ""
  echo -e "${YELLOW}トラブルシューティング:${NC}"
  echo "  1. ネットワーク接続を確認してください"
  echo "  2. API キーが正しく設定されているか確認してください"
  echo "  3. メモリ不足でないか確認してください"
  echo "  4. ログを確認してください: less $OUTPUT_PATH.log"
  exit 1
fi
