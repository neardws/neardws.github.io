#!/bin/bash
# 飞书妙记 API 封装脚本

set -e
source ~/User_Services/feishu/.env

# 获取 tenant_access_token
get_token() {
  curl -s -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
    -H 'Content-Type: application/json' \
    -d "{\"app_id\":\"$FEISHU_APP_ID\",\"app_secret\":\"$FEISHU_APP_SECRET\"}" \
    | jq -r '.tenant_access_token'
}

TOKEN=$(get_token)

case "$1" in
  list)
    # 获取妙记列表 (需要 user_access_token，暂用 tenant)
    curl -s -X GET 'https://open.feishu.cn/open-apis/minutes/v1/minutes' \
      -H "Authorization: Bearer $TOKEN" | jq .
    ;;
  get)
    # 获取妙记详情
    curl -s -X GET "https://open.feishu.cn/open-apis/minutes/v1/minutes/$2" \
      -H "Authorization: Bearer $TOKEN" | jq .
    ;;
  transcript)
    # 获取转写文本
    curl -s -X GET "https://open.feishu.cn/open-apis/minutes/v1/minutes/$2/transcript" \
      -H "Authorization: Bearer $TOKEN" | jq .
    ;;
  *)
    echo "Usage: $0 {list|get|transcript} [minute_token]"
    exit 1
    ;;
esac
