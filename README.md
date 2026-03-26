# SyosetuCrawler

將 [小説家になろう](https://syosetu.com/) 的小說依章節爬取並儲存為 txt 檔案。

## 安裝

```bash
pip install -r requirements.txt
```

## 使用方式

### 下載全部章節

```bash
python main.py
```

### 下載指定章節範圍

```bash
python main.py --chapters 1-10
```

### 指定輸出資料夾

支援相對路徑與絕對路徑：

```bash
# 相對路徑（相對於目前工作目錄）
python main.py --output my_output
python main.py --output novels/薬屋のひとりごと

# 絕對路徑
python main.py --output C:/Users/aries/Documents/novels
```

### 組合使用

```bash
python main.py --chapters 5-20 --output my_output
```

## 參數說明

| 參數 | 說明 | 預設值 |
|---|---|---|
| `--chapters START-END` | 下載指定章節範圍，例如 `1-10` | 全部章節 |
| `--output DIR` | 輸出資料夾路徑 | 專案資料夾下的 `output/` |

## 輸出格式

每個章節會儲存為獨立的 txt 檔案（UTF-8 編碼）：

```
output/
├── 0001_猫猫.txt
├── 0002_後宮.txt
└── ...
```

檔名格式為 `{章節編號（四位數）}_{章節標題}.txt`。

## 備註

- 若中途中斷，重新執行時會自動跳過已下載的章節
- 每次請求間隔 1 秒，避免對伺服器造成負擔
