#!/bin/bash
# 一键安装 IMA法律咨询专家
# 用法: ./install.sh [session-id]
# 或: WORKBUDDY_SESSION_ID=xxx ./install.sh

set -e

EXPERT_NAME="tencent-ima-copilot-legal-consultation"
TARGET_DIR="${HOME}/.workbuddy/plugins/marketplaces/my-experts/plugins/${EXPERT_NAME}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SESSION_ID="${1:-${WORKBUDDY_SESSION_ID}}"

echo "=== IMA法律咨询专家 安装 ==="
echo ""

# 1. 复制到目标目录
echo "[1/3] 复制到 ${TARGET_DIR}"
rm -rf "${TARGET_DIR}"
mkdir -p "$(dirname "${TARGET_DIR}")"
cp -r "${SCRIPT_DIR}" "${TARGET_DIR}"
echo "  ✅ 复制完成"

# 2. session-id（未提供则自动生成）
if [ -z "${SESSION_ID}" ]; then
    SESSION_ID=$(python3 -c "import uuid; print(uuid.uuid4())" 2>/dev/null || python -c "import uuid; print(str(uuid.uuid4()))" 2>/dev/null || uuidgen 2>/dev/null | tr '[:upper:]' '[:lower:]')
    echo "[2/3] 自动生成 session-id: ${SESSION_ID}"
else
    echo "[2/3] session-id: ${SESSION_ID}"
fi

# 3. 注册
echo "[3/3] 注册专家"
PYTHON=$(command -v python3 || command -v python)
if [ -z "${PYTHON}" ]; then
    echo "  ❌ 未找到 python3/python，请先安装 Python 3"
    exit 1
fi
PYTHONIOENCODING=utf-8 "${PYTHON}" "${TARGET_DIR}/scripts/register_expert.py" "${TARGET_DIR}" --session-id "${SESSION_ID}"
echo ""
echo "========================================"
echo "  🎉 IMA法律咨询专家 安装完成！"
echo "  重启 WorkBuddy 即可使用"
echo "========================================"
