#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub 图床上传脚本（URL 格式完全对齐
https://raw.githubusercontent.com/1638276310/imgs/master/xxx.jpg）
"""

import os
import sys
import json
import base64
import hashlib
import urllib.request as rq
from typing import List

# ==========  仅需修改以下 3 个值  ==========
TOKEN = 'Github Token'
USER  = 'username'
REPO  = 'repo'
BRANCH = 'master'
# ==========================================

API_URL = f'https://api.github.com/repos/{USER}/{REPO}/contents/'


def _b64(path: str) -> str:
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()


def upload(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    # 用前 16 位 sha256 当文件名，避免重复
    name = hashlib.sha256(open(path, 'rb').read()).hexdigest()[:16] + ext
    commit_msg = '由 寂寞沙洲冷 上传测试'

    data = {
        # 'message': f'upload {name}',
        'message': commit_msg,
        'content': _b64(path),
        'branch': BRANCH
    }

    req = rq.Request(API_URL + name, method='PUT')
    req.add_header('Authorization', f'token {TOKEN}')
    req.add_header('Content-Type', 'application/json')
    with rq.urlopen(req, data=json.dumps(data).encode()) as resp:
        if resp.status > 299:
            raise RuntimeError(resp.read().decode())

    return f'https://raw.githubusercontent.com/{USER}/{REPO}/{BRANCH}/{name}'


def main(paths: List[str]) -> None:
    for p in paths:
        try:
            url = upload(p)
            print(url)
        except Exception as e:
            print(f'❌ {p} 失败：{e}', file=sys.stderr)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python upload.py 1.jpg 2.png …')
        sys.exit(1)
    import glob
    files = []
    for pat in sys.argv[1:]:
        files.extend(glob.glob(pat))
    if not files:
        print('未匹配到任何文件')
        sys.exit(1)
    main(files)
