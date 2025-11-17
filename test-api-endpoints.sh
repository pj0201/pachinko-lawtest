#!/bin/bash

# APIエンドポイントテストスクリプト
BASE_URL="https://pachinko-lawtest.vercel.app"

echo "========================================="
echo "Pachinko Lawtest API テスト"
echo "========================================="
echo ""

# カラー設定
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# テスト1: ヘルスチェック
echo -e "${YELLOW}[テスト1] ヘルスチェック${NC}"
echo "GET $BASE_URL/api/health"
echo ""
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/health")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✅ 成功 (HTTP $http_code)${NC}"
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
else
    echo -e "${RED}❌ 失敗 (HTTP $http_code)${NC}"
    echo "$body"
fi
echo ""
echo "========================================="
echo ""

# テスト2: トークン検証（有効なトークン）
echo -e "${YELLOW}[テスト2] トークン検証 - 有効なトークン${NC}"
echo "POST $BASE_URL/api/validate-token"
echo "Body: {\"token\": \"039742a2-f799-4574-8530-a8e1d81960f1\", \"email\": \"test@example.com\"}"
echo ""
response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/validate-token" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "039742a2-f799-4574-8530-a8e1d81960f1",
    "email": "test@example.com"
  }')
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✅ 成功 (HTTP $http_code)${NC}"
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
else
    echo -e "${RED}❌ 失敗 (HTTP $http_code)${NC}"
    echo "$body"
fi
echo ""
echo "========================================="
echo ""

# テスト3: トークン検証（無効な形式）
echo -e "${YELLOW}[テスト3] トークン検証 - 無効な形式${NC}"
echo "POST $BASE_URL/api/validate-token"
echo "Body: {\"token\": \"INVALID_TOKEN\", \"email\": \"test@example.com\"}"
echo ""
response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/validate-token" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "INVALID_TOKEN",
    "email": "test@example.com"
  }')
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "400" ]; then
    echo -e "${GREEN}✅ 期待通りのエラー (HTTP $http_code)${NC}"
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
else
    echo -e "${RED}❌ 予期しないレスポンス (HTTP $http_code)${NC}"
    echo "$body"
fi
echo ""
echo "========================================="
echo ""

# テスト4: ユーザー登録（初回）
DEVICE_ID="test-device-$(date +%s)"
echo -e "${YELLOW}[テスト4] ユーザー登録 - 初回登録${NC}"
echo "POST $BASE_URL/api/register"
echo "Body: {\"email\": \"apitest1@example.com\", \"username\": \"APIテストユーザー1\", \"token\": \"039742a2-f799-4574-8530-a8e1d81960f1\", \"deviceId\": \"$DEVICE_ID\"}"
echo ""
response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"apitest1@example.com\",
    \"username\": \"APIテストユーザー1\",
    \"token\": \"039742a2-f799-4574-8530-a8e1d81960f1\",
    \"deviceId\": \"$DEVICE_ID\"
  }")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
    echo -e "${GREEN}✅ 成功 (HTTP $http_code)${NC}"
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
    FIRST_REGISTRATION_SUCCESS=true
else
    echo -e "${RED}❌ 失敗 (HTTP $http_code)${NC}"
    echo "$body"
    FIRST_REGISTRATION_SUCCESS=false
fi
echo ""
echo "========================================="
echo ""

# テスト5: 同じトークンで再登録（エラーが期待される）
if [ "$FIRST_REGISTRATION_SUCCESS" = true ]; then
    DEVICE_ID_2="test-device-2-$(date +%s)"
    echo -e "${YELLOW}[テスト5] ユーザー登録 - 同じトークンで再登録（エラー期待）${NC}"
    echo "POST $BASE_URL/api/register"
    echo "Body: {\"email\": \"apitest2@example.com\", \"username\": \"APIテストユーザー2\", \"token\": \"039742a2-f799-4574-8530-a8e1d81960f1\", \"deviceId\": \"$DEVICE_ID_2\"}"
    echo ""
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/register" \
      -H "Content-Type: application/json" \
      -d "{
        \"email\": \"apitest2@example.com\",
        \"username\": \"APIテストユーザー2\",
        \"token\": \"039742a2-f799-4574-8530-a8e1d81960f1\",
        \"deviceId\": \"$DEVICE_ID_2\"
      }")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "400" ]; then
        echo -e "${GREEN}✅ 期待通りのエラー (HTTP $http_code)${NC}"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"

        # エラーメッセージを確認
        if echo "$body" | grep -q "既に使用されています"; then
            echo -e "${GREEN}✅ 正しいエラーメッセージ: 「この招待URLは既に使用されています」${NC}"
        else
            echo -e "${YELLOW}⚠️  エラーメッセージが期待と異なります${NC}"
        fi
    else
        echo -e "${RED}❌ 予期しないレスポンス (HTTP $http_code)${NC}"
        echo "$body"
    fi
    echo ""
    echo "========================================="
    echo ""
else
    echo -e "${YELLOW}[テスト5] スキップ - テスト4が失敗したため${NC}"
    echo ""
fi

# テスト6: 同じメールアドレスで登録（エラーが期待される）
if [ "$FIRST_REGISTRATION_SUCCESS" = true ]; then
    DEVICE_ID_3="test-device-3-$(date +%s)"
    echo -e "${YELLOW}[テスト6] ユーザー登録 - 同じメールアドレスで登録（エラー期待）${NC}"
    echo "POST $BASE_URL/api/register"
    echo "Body: {\"email\": \"apitest1@example.com\", \"username\": \"APIテストユーザー3\", \"token\": \"cdfabd05-3fa5-4c49-87f0-a3a1aa03cdbb\", \"deviceId\": \"$DEVICE_ID_3\"}"
    echo ""
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/register" \
      -H "Content-Type: application/json" \
      -d "{
        \"email\": \"apitest1@example.com\",
        \"username\": \"APIテストユーザー3\",
        \"token\": \"cdfabd05-3fa5-4c49-87f0-a3a1aa03cdbb\",
        \"deviceId\": \"$DEVICE_ID_3\"
      }")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "400" ]; then
        echo -e "${GREEN}✅ 期待通りのエラー (HTTP $http_code)${NC}"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"

        # エラーメッセージを確認
        if echo "$body" | grep -q "既に登録されています"; then
            echo -e "${GREEN}✅ 正しいエラーメッセージ: 「このメールアドレスは既に登録されています」${NC}"
        else
            echo -e "${YELLOW}⚠️  エラーメッセージが期待と異なります${NC}"
        fi
    else
        echo -e "${RED}❌ 予期しないレスポンス (HTTP $http_code)${NC}"
        echo "$body"
    fi
    echo ""
    echo "========================================="
    echo ""
else
    echo -e "${YELLOW}[テスト6] スキップ - テスト4が失敗したため${NC}"
    echo ""
fi

# テスト7: 新しいトークン + 新しいメールで登録（成功が期待される）
DEVICE_ID_4="test-device-4-$(date +%s)"
echo -e "${YELLOW}[テスト7] ユーザー登録 - 新しいトークン + 新しいメール（成功期待）${NC}"
echo "POST $BASE_URL/api/register"
echo "Body: {\"email\": \"apitest3@example.com\", \"username\": \"APIテストユーザー3\", \"token\": \"d0b28ab3-44b6-45aa-897b-e72e0e0da116\", \"deviceId\": \"$DEVICE_ID_4\"}"
echo ""
response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"apitest3@example.com\",
    \"username\": \"APIテストユーザー3\",
    \"token\": \"d0b28ab3-44b6-45aa-897b-e72e0e0da116\",
    \"deviceId\": \"$DEVICE_ID_4\"
  }")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
    echo -e "${GREEN}✅ 成功 (HTTP $http_code)${NC}"
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
else
    echo -e "${RED}❌ 失敗 (HTTP $http_code)${NC}"
    echo "$body"
fi
echo ""
echo "========================================="
echo ""

echo -e "${GREEN}テスト完了！${NC}"
