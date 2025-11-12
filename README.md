````markdown
[English](//github.com/OGU4/ShakeScouter-NW/blob/main/README-en.md) | 日本語

# ShakeScouter-NW

**ShakeScouter-NW** は「サーモンラン NEXT WAVE」の映像を解析し、テレメトリを生成するための **OGU4 派生フォーク**です。
Ubuntu 24.04 / micromamba 環境（Python 3.12）で、モジュール実行 (`python -m`) による再現性の高い動作を前提に設計しています。

> 原作: [mntone/ShakeScouter](//github.com/mntone/ShakeScouter)

## 目次
- [特徴](#特徴)
- [要件](#要件)
- [インストール](#インストール)
- [使用例](#使用例)
  - [A. ROI 単体デバッグ](#a-roi-単体デバッグ)
  - [B. HDMI キャプチャ入力（推奨: ffmpeg → /dev/video10）](#b-hdmi-キャプチャ入力推奨-ffmpeg→devvideo10)
  - [C. mp4 ファイルを仮想カメラに流して解析](#c-mp4-ファイルを仮想カメラに流して解析)
- [起動方法](#起動方法)
- [起動オプション](#起動オプション)
- [トラブルシュート](#トラブルシュート)
- [ライセンス・謝辞](#ライセンス・謝辞)

## 特徴
- **モジュール起動方式を前提**：`python -m ShakeScouter.shakescout` で動作。`PYTHONPATH` 指定や相対起動不要。
- **実運用入力系**：`ffmpeg + v4l2loopback` による仮想カメラ `/dev/video10` 経由入力を想定。Rec.709／フルレンジ補正済み。
- **検出精度強化**：`WAVE` ロゴ検出の閾値調整（InRange V 下限緩和）でテンプレート一致性能改善。
- **デバッグ強化**：`--wave-debug` や `-t/-timestamp` による中間出力／ログ制御を標準化。

## 要件
- Ubuntu 24.04 LTS
- NVIDIA GPU（例：RTX 3060）＋対応ドライバ／CUDA 12.x（GPU利用時）
- ffmpeg, v4l2loopback モジュール
- Python 3.12 環境（micromamba 管理推奨）
- モジュール構成：`ShakeScouter/` フォルダに全ソースが集約済み

## インストール
```bash
# 1) リポジトリをクローン
git clone https://github.com/OGU4/ShakeScouter-NW.git
cd ShakeScouter-NW

# 2) micromamba 仮想環境を作成／有効化
micromamba create -n shakescouter python=3.12 -y
micromamba activate shakescouter

# 3) 依存関係
pip install -r requirements.txt

# 4) PyTorchのインストール（GPU使用環境／CPU使用環境を選択）
# GPUあり（例：cu124）
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
# GPUなし（CPU版）
# pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
````

## 使用例

### A. ROI 単体デバッグ

```bash
cd ShakeScouter
python -m ShakeScouter.roi_debug --device 10
# またはファイル入力
# python -m ShakeScouter.roi_debug --video /path/to/input.mp4
```

### B. HDMI キャプチャ入力（推奨：`/dev/video10` 経由）

1. 仮想カメラデバイス作成

```bash
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="ffmpeg_bridge" exclusive_caps=1
```

2. `/dev/video0` → `/dev/video10` へのブリッジ（1080p固定、色補正）

```bash
ffmpeg -f v4l2 -input_format yuyv422 -video_size 1920x1080 -framerate 60 -i /dev/video0 \
       -vf "scale=1920:1080:flags=lanczos,colorspace=all=bt709:iall=bt709:fast=1,scale=in_range=limited:out_range=full,format=yuv420p" \
       -pix_fmt yuv420p -f v4l2 /dev/video10
```

3. 解析実行（GPU使用例）

```bash
cd ShakeScouter
python -m ShakeScouter.shakescout -d cuda -i 10 --width 1920 --height 1080 -o console
```

> 注：`-i` は **入力カメラデバイス番号（整数）**。
> `-d` は **処理デバイス**（`auto`／`cpu`／`cuda`）。

### C. mp4 ファイルを仮想カメラに流して解析

```bash
ffmpeg -re -i input.mp4 \
       -vf "scale=1920:1080:flags=lanczos,colorspace=all=bt709:iall=bt709:fast=1,scale=in_range=limited:out_range=full,format=yuv420p" \
       -pix_fmt yuv420p -f v4l2 /dev/video10

cd ShakeScouter
python -m ShakeScouter.shakescout -d cuda -i 10 --width 1920 --height 1080 -o console
```

## 起動方法

```bash
python -m ShakeScouter.shakescout [options]
```

## 起動オプション

* `--development` : 開発モードで起動
* `-d, --device` : **処理デバイス**（`auto`／`cpu`／`cuda`）
* `-o, --outputs` : 出力方式（`console`／`json`／`websocket`）
* `-i, --input` : **入力カメラのデバイスID**（整数；例：10は `/dev/video10`）
* `--width`, `--height` : 入力解像度を指定（1080p前提推奨）
* `-t, --timestamp` : 出力 JSON にタイムスタンプを付与
* `-H, --host`, `-p, --port` : WebSocket 用ホスト／ポート
* `--wave-debug` : 解析中のデバッグログ・中間 PNG 出力を有効化（デフォルト OFF）

## トラブルシュート

* **映像が緑っぽい／白飛びする**：ブリッジ時に `colorspace=all=bt709:iall=bt709:fast=1,scale=in_range=limited:out_range=full` の指定があるか確認。
* **WAVE 検知が出ない**：`constants/screen.py` の InRange V 下限値が高すぎないか確認。
* **ROI がずれる／検知タイミングおかしい**：入力解像度を 1080p（1920x1080）に固定していないケースを確認。
* **VSCode F5 実行挙動がおかしい**：`.vscode/launch.json` が `module=ShakeScouter.shakescout`、`cwd=${workspaceFolder}` になっているか確認。

## ライセンス・謝辞

* ライセンス：GPLv3（原作に準拠）
* 原作： [mntone/ShakeScouter](//github.com/mntone/ShakeScouter)
* 本フォーク：OGU4 による実運用向け機能拡張を含む

最終更新：2025-11-12 (JST)
