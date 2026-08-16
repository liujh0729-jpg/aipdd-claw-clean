#!/usr/bin/env python3
"""
QQ邮箱 IMAP 邮件读取脚本
- 通过 IMAP 协议连接 QQ 邮箱
- 读取指定时间范围内的邮件
- 下载附件到本地
- 输出邮件信息 JSON 供后续处理
"""

import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
import json
import os
import sys
import re
import argparse
import base64
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path

# IMAP 配置（通过环境变量或命令行参数设置）
IMAP_SERVER = os.environ.get("MAIL_IMAP_SERVER", "imap.qq.com")
IMAP_PORT = 993

# 邮件配置（从环境变量或命令行参数获取）
DEFAULT_EMAIL = os.environ.get("MAIL_ADDR", "")
DEFAULT_AUTH_CODE = os.environ.get("MAIL_AUTH_CODE", "")

# 输出目录
PROJECT_ROOT = os.environ.get(
    "PROJECT_ROOT",
    os.path.expanduser("~")
)
DEFAULT_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "mails")


def decode_mime_header(header_value):
    """解码 MIME 编码的邮件头（主题、发件人等）"""
    if header_value is None:
        return ""
    
    decoded_parts = []
    parts = decode_header(header_value)
    
    for content, charset in parts:
        if isinstance(content, bytes):
            try:
                if charset:
                    decoded_parts.append(content.decode(charset, errors='replace'))
                else:
                    # 尝试多种编码
                    for enc in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                        try:
                            decoded_parts.append(content.decode(enc))
                            break
                        except (UnicodeDecodeError, LookupError):
                            continue
                    else:
                        decoded_parts.append(content.decode('utf-8', errors='replace'))
            except Exception:
                decoded_parts.append(str(content))
        else:
            decoded_parts.append(content)
    
    return ''.join(decoded_parts)


def sanitize_filename(name, max_len=50):
    """清理文件名，去除非法字符"""
    # 移除或替换非法字符
    name = re.sub(r'[\\/:*?"<>|\r\n\t]', '_', name)
    name = re.sub(r'_+', '_', name)
    name = name.strip('_. ')
    if len(name) > max_len:
        name = name[:max_len].rstrip('_. ')
    return name or "untitled"


def get_email_body(msg):
    """提取邮件正文，返回 (text_body, html_body) 元组"""
    text_body = ""
    html_body = ""
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))
            
            # 跳过附件
            if "attachment" in content_disposition:
                continue
            
            try:
                payload = part.get_payload(decode=True)
                if payload is None:
                    continue
                    
                charset = part.get_content_charset() or 'utf-8'
                decoded = payload.decode(charset, errors='replace')
                
                if content_type == "text/plain":
                    text_body += decoded
                elif content_type == "text/html":
                    html_body += decoded
            except Exception:
                continue
    else:
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or 'utf-8'
                decoded = payload.decode(charset, errors='replace')
                if msg.get_content_type() == "text/html":
                    html_body = decoded
                else:
                    text_body = decoded
        except Exception:
            pass
    
    return text_body.strip(), html_body.strip()


def get_body_text(text_body, html_body):
    """从纯文本和 HTML 中生成可读正文"""
    if text_body:
        return text_body
    
    if html_body:
        clean = re.sub(r'<style[^>]*>.*?</style>', '', html_body, flags=re.DOTALL)
        clean = re.sub(r'<script[^>]*>.*?</script>', '', clean, flags=re.DOTALL)
        clean = re.sub(r'<[^>]+>', '', clean)
        clean = re.sub(r'&nbsp;', ' ', clean)
        clean = re.sub(r'&lt;', '<', clean)
        clean = re.sub(r'&gt;', '>', clean)
        clean = re.sub(r'&amp;', '&', clean)
        clean = re.sub(r'\n{3,}', '\n\n', clean)
        return clean.strip()
    
    return "(无可提取的正文内容)"


def save_email_images(msg, html_body, save_dir):
    """保存邮件中的所有图片（CID内联、外链URL、Base64嵌入）
    
    Returns:
        保存的图片列表 [{filename, path, size, source}, ...]
    """
    saved_images = []
    img_counter = [0]  # 用列表以便在闭包中修改
    images_subdir = os.path.join(save_dir, "images")
    
    def next_img_name(ext=".png"):
        img_counter[0] += 1
        return f"img_{img_counter[0]:03d}{ext}"
    
    # === 1. CID 内联图片（MIME 部分） ===
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_id = part.get("Content-ID", "")
            content_disp = str(part.get("Content-Disposition", ""))
            
            # 图片类型且非普通附件
            if not content_type.startswith("image/"):
                continue
            if "attachment" in content_disp and not content_id:
                continue  # 纯附件，跳过
            
            try:
                payload = part.get_payload(decode=True)
                if not payload or len(payload) < 100:
                    continue  # 太小的跳过（可能是占位符）
                
                ext = "." + content_type.split("/")[-1] if "/" in content_type else ".png"
                if ext == ".jpeg":
                    ext = ".jpg"
                filename = next_img_name(ext)
                filepath = os.path.join(images_subdir, filename)
                
                os.makedirs(images_subdir, exist_ok=True)
                with open(filepath, 'wb') as f:
                    f.write(payload)
                saved_images.append({
                    "filename": filename,
                    "path": filepath,
                    "size": len(payload),
                    "source": "cid",
                    "content_id": content_id
                })
            except Exception:
                continue
    
    # === 2. HTML 中的外链图片 ===
    if html_body:
        img_urls = re.findall(r'<img[^>]+src=["\'](https?://[^"\'>]+)["\']', html_body, re.IGNORECASE)
        
        for url in img_urls:
            try:
                # 跳过常见的跟踪像素和极小图片
                if any(skip in url.lower() for skip in ['pixel', 'spacer', 'blank.gif', '1x1', 'tracking']):
                    continue
                
                req = urllib.request.Request(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
                })
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = resp.read()
                
                if len(data) < 200:
                    continue  # 太小，跳过
                
                # 从 URL 或 Content-Type 推断扩展名
                ct = resp.headers.get('Content-Type', '')
                if 'jpeg' in ct or 'jpg' in ct:
                    ext = ".jpg"
                elif 'png' in ct:
                    ext = ".png"
                elif 'gif' in ct:
                    ext = ".gif"
                elif 'webp' in ct:
                    ext = ".webp"
                elif 'svg' in ct:
                    ext = ".svg"
                else:
                    # 从 URL 路径推断
                    url_path = url.split('?')[0]
                    ext = os.path.splitext(url_path)[1] or ".png"
                    if ext.lower() not in ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp'):
                        ext = ".png"
                if ext == ".jpeg":
                    ext = ".jpg"
                
                filename = next_img_name(ext)
                os.makedirs(images_subdir, exist_ok=True)
                filepath = os.path.join(images_subdir, filename)
                with open(filepath, 'wb') as f:
                    f.write(data)
                saved_images.append({
                    "filename": filename,
                    "path": filepath,
                    "size": len(data),
                    "source": "url",
                    "url": url[:200]
                })
            except Exception:
                continue
        
        # === 3. Base64 嵌入图片 ===
        b64_pattern = re.compile(
            r'<img[^>]+src=["\']data:image/([^;]+);base64,([A-Za-z0-9+/=\s]+)["\']',
            re.IGNORECASE
        )
        for match in b64_pattern.finditer(html_body):
            try:
                img_format = match.group(1).lower()
                b64_data = match.group(2).replace('\s', '')
                data = base64.b64decode(b64_data)
                
                if len(data) < 100:
                    continue
                
                ext = "." + img_format if img_format else ".png"
                if ext == ".jpeg":
                    ext = ".jpg"
                filename = next_img_name(ext)
                os.makedirs(images_subdir, exist_ok=True)
                filepath = os.path.join(images_subdir, filename)
                with open(filepath, 'wb') as f:
                    f.write(data)
                saved_images.append({
                    "filename": filename,
                    "path": filepath,
                    "size": len(data),
                    "source": "base64"
                })
            except Exception:
                continue
    
    return saved_images


def save_attachments(msg, save_dir):
    """保存邮件附件到指定目录，返回保存的文件列表"""
    saved_files = []
    
    if not msg.is_multipart():
        return saved_files
    
    for part in msg.walk():
        content_disposition = str(part.get("Content-Disposition", ""))
        
        if "attachment" not in content_disposition:
            continue
        
        filename = part.get_filename()
        if filename:
            filename = decode_mime_header(filename)
        else:
            # 尝试从 content-type 获取文件名
            content_type = part.get_content_type()
            ext = content_type.split('/')[-1] if '/' in content_type else 'bin'
            filename = f"attachment.{ext}"
        
        filename = sanitize_filename(filename, max_len=100)
        filepath = os.path.join(save_dir, filename)
        
        # 避免覆盖
        if os.path.exists(filepath):
            base, ext = os.path.splitext(filepath)
            i = 1
            while os.path.exists(f"{base}_{i}{ext}"):
                i += 1
            filepath = f"{base}_{i}{ext}"
        
        try:
            payload = part.get_payload(decode=True)
            if payload:
                with open(filepath, 'wb') as f:
                    f.write(payload)
                saved_files.append({
                    "filename": os.path.basename(filepath),
                    "path": filepath,
                    "size": len(payload)
                })
        except Exception as e:
            print(f"  [警告] 附件保存失败: {filename} - {e}", file=sys.stderr)
    
    return saved_files


def fetch_emails(email_addr, auth_code, since_date, until_date=None, folder="INBOX", output_dir=None):
    """
    连接 IMAP 服务器并获取邮件
    
    Args:
        email_addr: QQ 邮箱地址
        auth_code: IMAP 授权码
        since_date: 起始日期 (datetime)
        until_date: 截止日期 (datetime, 默认今天)
        folder: 邮件文件夹
        output_dir: 附件输出目录
    
    Returns:
        邮件信息列表 (dict)
    """
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"[连接] {IMAP_SERVER}:{IMAP_PORT} ...", file=sys.stderr)
    
    # 连接 IMAP
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(email_addr, auth_code)
    print(f"[登录成功] {email_addr}", file=sys.stderr)
    
    # 选择文件夹
    status, folders = mail.list()
    print(f"[可用文件夹]", file=sys.stderr)
    for f in folders[:10]:
        print(f"  {f.decode('utf-8', errors='replace')}", file=sys.stderr)
    
    mail.select(folder, readonly=True)
    
    # 使用 REVERSE 顺序获取（最新邮件优先）
    # 注意：QQ IMAP 的 SINCE 过滤可能不可靠，需要客户端二次过滤
    status, data = mail.search(None, 'ALL')
    if status != 'OK':
        print("[错误] 搜索失败", file=sys.stderr)
        mail.logout()
        return []
    
    all_ids = data[0].split()
    print(f"[总邮件数] {len(all_ids)}", file=sys.stderr)
    
    # 倒序处理（最新邮件优先）
    email_ids = list(reversed(all_ids))
    
    # 计算截止时间
    if until_date is None:
        until_date = datetime.now() + timedelta(days=1)
    
    emails = []
    skipped_old = 0
    max_to_scan = min(len(email_ids), 500)  # 最多扫描500封以控制时间
    
    for eid in email_ids[:max_to_scan]:
        try:
            # 先只获取头部做日期判断
            status, header_data = mail.fetch(eid, '(BODY.PEEK[HEADER])')
            if status != 'OK':
                continue
            
            header_msg = email.message_from_bytes(header_data[0][1])
            date_str_header = header_msg.get("Date", "")
            
            try:
                email_date = parsedate_to_datetime(date_str_header)
                # 统一去掉时区信息，方便与本地 naive datetime 比较
                if email_date.tzinfo is not None:
                    email_date = email_date.replace(tzinfo=None)
            except Exception:
                email_date = None
            
            # 客户端日期过滤
            if email_date:
                if email_date < since_date:
                    skipped_old += 1
                    # 如果连续跳过10封老邮件，认为后面的都更老，提前结束
                    if skipped_old >= 10:
                        print(f"[提前结束] 已连续跳过 {skipped_old} 封老邮件", file=sys.stderr)
                        break
                    continue
                if email_date > until_date:
                    continue
                skipped_old = 0  # 重置连续跳过计数
            
            # 日期在范围内，获取完整邮件
            status, msg_data = mail.fetch(eid, '(RFC822)')
            if status != 'OK':
                continue
            
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            # 解析邮件头
            subject = decode_mime_header(msg.get("Subject", ""))
            from_addr = decode_mime_header(msg.get("From", ""))
            to_addr = decode_mime_header(msg.get("To", ""))
            date_str = msg.get("Date", "")
            cc_addr = decode_mime_header(msg.get("Cc", ""))
            
            # 解析日期
            try:
                email_date = parsedate_to_datetime(date_str)
                if email_date.tzinfo is not None:
                    email_date = email_date.replace(tzinfo=None)
                date_formatted = email_date.strftime("%Y-%m-%d %H:%M:%S")
                date_short = email_date.strftime("%Y%m%d_%H%M")
            except Exception:
                email_date = None
                date_formatted = date_str
                date_short = datetime.now().strftime("%Y%m%d_%H%M")
            
            # 提取正文（纯文本 + HTML）
            text_body, html_body = get_email_body(msg)
            body = get_body_text(text_body, html_body)
            # 截取前 3000 字符用于摘要
            body_preview = body[:3000] if len(body) > 3000 else body
            
            # 创建邮件目录
            safe_subject = sanitize_filename(subject, max_len=40)
            dir_name = f"{date_short}_{safe_subject}"
            mail_dir = os.path.join(output_dir, dir_name)
            os.makedirs(mail_dir, exist_ok=True)
            
            # 保存附件
            attachments = save_attachments(msg, mail_dir)
            
            # 保存正文中的图片（CID内联 + 外链 + Base64）
            inline_images = save_email_images(msg, html_body, mail_dir)
            
            email_info = {
                "id": eid.decode() if isinstance(eid, bytes) else str(eid),
                "subject": subject,
                "from": from_addr,
                "to": to_addr,
                "cc": cc_addr,
                "date": date_formatted,
                "body_preview": body_preview,
                "body_length": len(body),
                "attachments": attachments,
                "inline_images": inline_images,
                "output_dir": mail_dir,
                "has_attachments": len(attachments) > 0,
                "has_images": len(inline_images) > 0
            }
            emails.append(email_info)
            
            att_info = f" | 附件: {len(attachments)}" if attachments else ""
            img_info = f" | 图片: {len(inline_images)}" if inline_images else ""
            print(f"  [{date_formatted}] {subject[:40]}{att_info}{img_info}", file=sys.stderr)
            
        except Exception as e:
            print(f"  [警告] 邮件 {eid} 处理失败: {e}", file=sys.stderr)
            continue
    
    mail.logout()
    print(f"\n[完成] 共处理 {len(emails)} 封邮件", file=sys.stderr)
    
    return emails


def main():
    parser = argparse.ArgumentParser(description="QQ邮箱 IMAP 邮件读取工具")
    parser.add_argument("--email", default=DEFAULT_EMAIL, help="QQ邮箱地址")
    parser.add_argument("--auth-code", default=DEFAULT_AUTH_CODE, help="IMAP授权码")
    parser.add_argument("--since", required=False, help="起始日期 YYYY-MM-DD (默认7天前)")
    parser.add_argument("--until", required=False, help="截止日期 YYYY-MM-DD (默认今天)")
    parser.add_argument("--days", type=int, default=7, help="读取最近N天的邮件 (默认7)")
    parser.add_argument("--folder", default="INBOX", help="邮件文件夹 (默认 INBOX)")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="输出目录")
    parser.add_argument("--limit", type=int, default=100, help="最大邮件数量")
    parser.add_argument("--body-length", type=int, default=3000, help="正文截取长度")
    
    args = parser.parse_args()
    
    # 计算日期范围
    if args.since:
        since_date = datetime.strptime(args.since, "%Y-%m-%d")
    else:
        since_date = datetime.now() - timedelta(days=args.days)
    
    until_date = None
    if args.until:
        until_date = datetime.strptime(args.until, "%Y-%m-%d") + timedelta(days=1)
    
    print(f"[配置]", file=sys.stderr)
    print(f"  邮箱: {args.email}", file=sys.stderr)
    print(f"  时间范围: {since_date.strftime('%Y-%m-%d')} ~ {(until_date or datetime.now()).strftime('%Y-%m-%d')}", file=sys.stderr)
    print(f"  输出目录: {args.output_dir}", file=sys.stderr)
    print(f"  文件夹: {args.folder}", file=sys.stderr)
    print("", file=sys.stderr)
    
    # 获取邮件
    emails = fetch_emails(
        email_addr=args.email,
        auth_code=args.auth_code,
        since_date=since_date,
        until_date=until_date,
        folder=args.folder,
        output_dir=args.output_dir
    )
    
    # 截取正文长度
    for e in emails:
        if len(e["body_preview"]) > args.body_length:
            e["body_preview"] = e["body_preview"][:args.body_length] + "..."
    
    # 输出 JSON 到 stdout
    output = {
        "total": len(emails),
        "since": since_date.strftime("%Y-%m-%d"),
        "until": (until_date or datetime.now()).strftime("%Y-%m-%d"),
        "output_dir": args.output_dir,
        "emails": emails
    }
    
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
