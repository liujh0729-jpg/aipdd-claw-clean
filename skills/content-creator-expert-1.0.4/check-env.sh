#!/bin/bash

echo "========================================"
echo "  内容创作专家 Skill - 环境检查"
echo "========================================"

check_pass() {
    echo "✅ $1"
}

check_warn() {
    echo "⚠️  $1"
}

check_fail() {
    echo "❌ $1"
}

echo ""
echo "--- 基础环境 ---"
if command -v node >/dev/null 2>&1; then
    NODE_VER=$(node --version)
    check_pass "Node.js $NODE_VER"
else
    check_fail "Node.js 未安装（AI视频、PPT需要v20+）"
fi

if command -v python3 >/dev/null 2>&1; then
    PY_VER=$(python3 --version | awk '{print $2}')
    check_pass "Python3: $PY_VER"
else
    check_fail "Python3 未安装（工具集脚本需要）"
fi

echo ""
echo "--- 系统依赖 ---"
if command -v ffmpeg >/dev/null 2>&1; then
    check_pass "ffmpeg 已安装"
else
    check_warn "ffmpeg 未安装（视频处理需要，运行: brew install ffmpeg）"
fi

if command -v qpdf >/dev/null 2>&1; then
    check_pass "qpdf 已安装"
else
    check_warn "qpdf 未安装（大PDF分割需要，运行: brew install qpdf）"
fi

echo ""
echo "--- Python包 ---"
if python3 -c "import imapclient" 2>/dev/null; then
    check_pass "imapclient 已安装"
else
    check_warn "imapclient 未安装（邮件读取需要，运行: pip3 install imapclient）"
fi

if python3 -c "import pypdf" 2>/dev/null; then
    check_pass "pypdf 已安装"
else
    check_warn "pypdf 未安装（PDF处理需要，运行: pip3 install pypdf）"
fi

echo ""
echo "--- 可选工具 ---"
if command -v xparse-cli >/dev/null 2>&1; then
    check_pass "xparse-cli 已安装（文档解析）"
else
    check_warn "xparse-cli 未安装（文档解析，运行安装脚本，免费版支持PDF/图片）"
fi

if [ -d "/Applications/Google Chrome.app" ] || [ -d "/Applications/Microsoft Edge.app" ] || [ -d "/Applications/Chromium.app" ]; then
    check_pass "Chrome/Edge 已安装（PPT导出需要）"
else
    check_warn "Chrome/Edge 未找到（PPT导出PPTX/PDF需要）"
fi

echo ""
echo "--- AI营销视频配置 ---"
if [ -n "$NEWAPI_BASE_URL" ] && [ -n "$NEWAPI_API_KEY" ]; then
    check_pass "NEWAPI 已配置（AI营销视频生成）"
else
    check_warn "NEWAPI 未配置（使用AI视频生成功能需要，见CONFIG.md）"
fi

echo ""
echo "--- PPT配置 ---"
if [ -n "$DASHI_PPT_PROJECT_PATH" ] && [ -f "$DASHI_PPT_PROJECT_PATH/package.json" ]; then
    check_pass "DASHI_PPT_PROJECT_PATH 已配置（PPT制作）"
else
    check_warn "DASHI_PPT_PROJECT_PATH 未配置（使用PPT功能需要，见CONFIG.md）"
fi

echo ""
echo "--- 可选API配置 ---"
if [ -n "$DASHSCOPE_API_KEY" ]; then
    check_pass "DASHSCOPE_API_KEY 已配置（视频学习分析）"
else
    check_warn "DASHSCOPE_API_KEY 未配置（视频学习分析需要，可选）"
fi

if [ -n "$MAIL_ADDR" ]; then
    check_pass "邮件配置 已配置（$MAIL_ADDR）"
else
    check_warn "邮件配置 未配置（邮件读取需要，可选）"
fi

echo ""
echo "========================================"
PASS=0
WARN=0
FAIL=0
echo "检查完成。"
echo ""
echo "详细配置指南请查看: CONFIG.md"
echo "使用说明请查看: README.md"
