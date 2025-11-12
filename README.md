[English](//github.com/OGU4/ShakeScouter-NW/blob/main/README-en.md) | 日本語

# ShakeScouter-NW

**ShakeScouter-NW** は「サーモンラン NEXT WAVE」の映像を解析し、テレメトリを生成するための **OGU4 派生フォーク**です。  
Ubuntu 24.04 / micromamba / NVIDIA RTX 3060 (CUDA 12.x) での実運用を前提に、色空間補正・仮想カメラ経由の安定動作・デバッグ性を強化しています。

> 原作: [mntone/ShakeScouter](//github.com/mntone/ShakeScouter)

## 目次
- [特徴](#特徴)
- [要件](#要件)
- [インストール](#インストール)
- [使用例](#使用例)
  - [A. ROI 単体デバッグ](#a-roi-単体デバッグ)
  - [B. HDMI キャプチャ入力（推奨: ffmpeg→/dev/video10）](#b-hdmi-キャプチャ入力推奨-ffmpegdevvideo10)
  - [C. mp4 ファイルを仮想カメラに流して解析](#c-mp4-ファイルを仮想カメラに流して解析)
- [起動オプション](#起動オプション)
- [トラブルシュート](#トラブルシュート)
- [ライセンス・謝辞](#ライセンス謝辞)

## 特徴
- **実運用前提の入力系**: ffmpeg + v4l2loopback で `/dev/video0 → /dev/video10` にブリッジし、Rec.709/フルレンジへ補正して「緑化」を防止。
- **検出安定化**: `WAVE` ロゴの抽出閾値を見直し（InRange: V下限を緩和）テンプレート一致精度を改善。
- **静粛なデバッグ**: `--wave-debug` でデバッグログ／中間PNGの出力をトグル（デフォルトOFF）。

## 要件
- Ubuntu 24.04 LTS
- NVIDIA GPU（例: RTX 3060）と対応ドライバ
- ffmpeg, v4l2loopback
- Python 3.12 / micromamba

## インストール

```bash
# 1) クローン
git clone https://github.com/OGU4/ShakeScouter-NW.git
cd ShakeScouter-NW

# 2) micromamba 環境（例）
micromamba create -n shakescouter python=3.12 -y
micromamba activate shakescouter

# 3) 依存関係
pip install -r requirements.txt

# 4) PyTorch (CUDA あり/なしのどちらかを選択)
# CUDA対応（推奨・環境に応じて cuXXX を選択。例は cu124）
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
# CPU版（GPU非使用の場合）
# pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
````

## 使用例

### A. ROI 単体デバッグ

`ShakeScouter/roi_debug.py` は 1 フレームを取り出して WAVE 抽出パイプを検証します。

```bash
cd ShakeScouter
PYTHONPATH=.. python roi_debug.py --device 10           # /dev/video10 を読む
# またはファイル
# PYTHONPATH=.. python roi_debug.py --video /path/to/input.mp4
```

### B. HDMI キャプチャ入力（推奨: ffmpeg→/dev/video10）

1. 仮想カメラ作成

```bash
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="ffmpeg_bridge" exclusive_caps=1
```

2. `/dev/video0` → `/dev/video10` へブリッジ（緑化防止・1080p固定）

```bash
ffmpeg -f v4l2 -input_format yuyv422 -video_size 1920x1080 -framerate 60 -i /dev/video0 \
       -vf "scale=1920:1080:flags=lanczos,colorspace=all=bt709:iall=bt709:fast=1,scale=in_range=limited:out_range=full,format=yuv420p" \
       -pix_fmt yuv420p -f v4l2 /dev/video10
```

3. 解析を実行（GPU/CUDA 使用）

```bash
cd ShakeScouter
PYTHONPATH=.. python shakescout.py -d cuda -i 10 --width 1920 --height 1080 -o console
```

> 注: `-i` は **カメラのデバイス番号（整数）**。
> `-d` は **計算デバイス**（auto/cpu/cuda）で、カメラではありません。

### C. mp4 ファイルを仮想カメラに流して解析

```bash
ffmpeg -re -i input.mp4 \
       -vf "scale=1920:1080:flags=lanczos,colorspace=all=bt709:iall=bt709:fast=1,scale=in_range=limited:out_range=full,format=yuv420p" \
       -pix_fmt yuv420p -f v4l2 /dev/video10

cd ShakeScouter
PYTHONPATH=.. python shakescout.py -d cuda -i 10 --width 1920 --height 1080 -o console
```

## 起動オプション

`py shakescout.py [options]`

* `--development` : 開発モードで起動
* `-d, --device` : **計算デバイス** (`auto` / `cpu` / `cuda`)
* `-o, --outputs` : 出力方式 (`console` / `json` / `websocket`)
* `-i, --input` : **入力カメラのデバイスID**（整数; 例: `10` は `/dev/video10`）
* `--width`, `--height` : 入力の解像度（1080p前提を推奨）
* `-t, --timestamp` : JSON ファイル名に日時を付与
* `-H, --host`, `-p, --port` : WebSocket 用ホスト/ポート
* `--wave-debug` : 解析中のデバッグログ・中間PNGを有効化（デフォルトOFF）

## トラブルシュート

* **映像が緑っぽい/白飛び**: 上記 ffmpeg の `colorspace` と `scale=in_range=limited:out_range=full` を必ず適用。
* **WAVE 検知が出ない**: `constants/screen.py` の `InRange` の V 下限が高すぎないか確認（例: `lower=[0,0,200]`）。
* **ROI がずれる**: 1080p 以外の解像度で入力していないか確認。
* **ログがうるさい**: `--wave-debug` を外す。

## ライセンス・謝辞

* ライセンス: GPLv3（原作に準拠）
* 原作: [mntone/ShakeScouter](//github.com/mntone/ShakeScouter)
* 本フォークは OGU4 による実運用向け改修を含みます。

最終更新: 2025-11-12 (JST)
