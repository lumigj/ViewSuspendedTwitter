# ViewSuspendedTwitter

![Sample](sample/Screenshot%202026-02-08%20202953.png)

- [English](#english)
- [中文](#中文)

## English

This project fetches archived Twitter snapshots from the Wayback Machine and renders them into simplified HTML.

### Project Structure

- `script.py`: Fetches `[timestamp, original]` rows from the CDX API and writes them into a SQLite database.
- `run_pipeline.py`: Reads pending rows from the database, downloads snapshots, and saves HTML files.
- `snapshot.py`: Snapshot fetching + HTML simplification utilities.
- `output/`: Output directory for the database and generated HTML files.

### Usage

1. Update `username` in `run_pipeline.py`.
2. Run:

```bash
python run_pipeline.py
```

On first run it creates `output/{username}.db` and seeds it with snapshot rows.

### Database

File: `output/{username}.db`

Table: `snapshots`

Columns:

- `timestamp`: Wayback snapshot timestamp
- `original`: Original URL
- `status`:
  - `0`: not processed
  - `1`: success
  - `2`: failed
- `error`: failure reason (`NULL` on success)

`run_pipeline.py` reads rows with `status IN (0, 2)` so failed rows are retried.

### Output

Successful runs write HTML files under `output/{username}/`. Filenames include the `timestamp` and a sanitized `original`.

### Notes

Wayback may throttle or temporarily reject requests. If you hit failures, re-run `run_pipeline.py` to retry.

## 中文

本项目用于从 Wayback Machine 获取指定 Twitter 用户推文快照，并把快照内容整理成简化 HTML。

### 目录结构

- `script.py`：负责从 CDX 接口拉取 `[timestamp, original]` 列表，并写入 SQLite 数据库。
- `run_pipeline.py`：读取数据库中的待处理记录，逐条抓取快照并保存为 HTML。
- `snapshot.py`：封装快照抓取与 HTML 简化逻辑。
- `output/`：输出目录，包含数据库文件和生成的 HTML。

### 使用方法

1. 修改 `run_pipeline.py` 中的 `username`。
2. 运行：

```bash
python run_pipeline.py
```

首次运行会自动创建 `output/{username}.db` 并写入快照列表。

### 数据库说明

数据库文件：`output/{username}.db`

表：`snapshots`

字段说明：

- `timestamp`：Wayback 快照时间戳
- `original`：原始 URL
- `status`：
  - `0`：未处理
  - `1`：抓取成功
  - `2`：抓取失败
- `error`：失败原因（成功时为 `NULL`）

`run_pipeline.py` 会读取 `status IN (0, 2)` 的记录，失败的会被再次尝试。

### 输出

成功抓取后会在 `output/{username}/` 下生成 HTML 文件，文件名包含 `timestamp` 和 `original` 的安全化版本。

### 备注

Wayback 可能有访问限制或临时不可用。如果遇到失败，可多次运行 `run_pipeline.py` 继续重试。
