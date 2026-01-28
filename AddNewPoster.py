#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AddNewPoster.py
画像をA4比率でリサイズ・圧縮してギャラリーに追加し、index.htmlを自動生成してpush
"""

import sys
import os
from PIL import Image
import subprocess

# 設定
TARGET_WIDTH = 595
TARGET_HEIGHT = 842
A4_RATIO = 1 / 1.41421356  # 0.707
RATIO_TOLERANCE = 0.02  # 許容誤差2%
JPEG_QUALITY = 90
WORK_DIR = os.path.dirname(os.path.abspath(__file__))

def check_a4_ratio(img):
    """A4比率かチェック"""
    width, height = img.size
    ratio = width / height
    return abs(ratio - A4_RATIO) < RATIO_TOLERANCE

def convert_image(input_path):
    """画像を変換して保存"""
    img = Image.open(input_path)
    
    # A4比率チェック
    if not check_a4_ratio(img):
        ratio = img.size[0] / img.size[1]
        print(f"エラー: A4比率ではありません")
        print(f"  入力画像: {img.size[0]}x{img.size[1]} (比率: {ratio:.3f})")
        print(f"  期待比率: {A4_RATIO:.3f} (許容誤差: ±{RATIO_TOLERANCE})")
        sys.exit(1)
    
    # リサイズ
    img_resized = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.LANCZOS)
    
    # RGB変換（RGBA対策）
    if img_resized.mode in ('RGBA', 'P'):
        img_resized = img_resized.convert('RGB')
    
    # 出力パス
    basename = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(WORK_DIR, f"{basename}.jpg")
    
    # 保存
    img_resized.save(output_path, 'JPEG', quality=JPEG_QUALITY)
    print(f"変換完了: {output_path}")
    return output_path

def generate_index_html():
    """index.htmlを画像一覧から自動生成"""
    # 画像ファイル一覧取得
    extensions = ('.jpg', '.jpeg', '.png')
    images = [f for f in os.listdir(WORK_DIR) 
              if f.lower().endswith(extensions) and not f.startswith('.')]
    images.sort()
    
    # カード生成
    cards = []
    for img_file in images:
        name = os.path.splitext(img_file)[0]
        # 先頭アンダースコア除去して表示名に
        display_name = name.lstrip('_')
        card = f"""            <div class="image-card">
                <h3>{display_name}</h3>
                <img src="{img_file}" alt="{display_name} Poster">
                <div class="url-display">
                    https://pandrabox.github.io/FlatMeetup/{img_file}
                </div>
            </div>"""
        cards.append(card)
    
    # HTML生成
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FlatMeetup Posters</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            color: #333;
        }}
        .gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .image-card {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 15px;
            text-align: center;
        }}
        .image-card img {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }}
        .image-card h3 {{
            margin: 10px 0 5px 0;
            color: #333;
        }}
        .url-display {{
            background: #f8f9fa;
            padding: 8px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 12px;
            word-break: break-all;
            margin-top: 10px;
            border: 1px solid #e9ecef;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>FlatMeetup Posters</h1>
        <p style="text-align: center;">VRChat用ポスター画像集</p>
        
        <div class="gallery">
{chr(10).join(cards)}
        </div>
    </div>
</body>
</html>
"""
    
    index_path = os.path.join(WORK_DIR, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"index.html 生成完了: {len(images)}枚の画像")
    return index_path

def git_push(message):
    """git add, commit, push"""
    os.chdir(WORK_DIR)
    
    # add
    result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode != 0:
        print(f"git add 失敗: {result.stderr}")
        sys.exit(1)
    
    # commit
    result = subprocess.run(['git', 'commit', '-m', message], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode != 0:
        if 'nothing to commit' in result.stdout or 'nothing to commit' in result.stderr:
            print("変更なし、pushスキップ")
            return
        print(f"git commit 失敗: {result.stderr}")
        sys.exit(1)
    
    # push
    result = subprocess.run(['git', 'push'], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode != 0:
        print(f"git push 失敗: {result.stderr}")
        sys.exit(1)
    
    print("git push 完了")

def main():
    if len(sys.argv) < 2:
        print("使用法: python AddNewPoster.py <画像パス>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    if not os.path.exists(input_path):
        print(f"エラー: ファイルが見つかりません: {input_path}")
        sys.exit(1)
    
    # 画像変換
    output_path = convert_image(input_path)
    
    # index.html生成
    generate_index_html()
    
    # git push
    basename = os.path.basename(output_path)
    git_push(f"Add {basename}")
    
    print("完了！")

if __name__ == '__main__':
    main()
