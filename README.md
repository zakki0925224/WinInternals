# WinInternals

Windows低レイヤープログラミングの勉強用リポジトリ。エクスプロイト用コードも含まれているため、実行には細心の注意を払うこと。

## 免責事項

- このリポジトリは学習目的のみを対象としています。
- すべてのコードは管理された環境でWindowsの内部構造を理解するためのものです。
- 不正アクセスや悪意のある活動への使用を禁じます。

## 環境

- **開発**: Windows（ホスト） + Visual Studio + CMake
- **実行**: Windows VM（ネットワークファイル共有経由でアクセス）
- **デバッガ**: WinDbg Preview（VM側）

## ディレクトリ構成

| ディレクトリ    | 内容                                                                 |
| --------------- | -------------------------------------------------------------------- |
| `exploitation/` | エクスプロイトのサンプルコード。カテゴリごとにサブディレクトリで分類 |
| `internals/`    | Windows内部構造のサンプルコード                                      |
| `cheatsheets/`  | チートシートリファレンス                                             |
| `common/`       | 共通ヘッダ・CMakeモジュール・Pythonユーティリティ                    |
| `scripts/`      | その他スクリプト                                                     |
| `build/`        | ビルド出力（gitignore対象）                                          |
| `work/`         | デプロイ出力（gitignore対象）                                        |

各プロジェクトは `main.c` + `CMakeLists.txt` で構成され、エクスプロイト対象には `exploit.py` が付属する。

## ビルドとデプロイ

コマンドプロンプトからリポジトリルートで実行する。VS環境のセットアップ・x86/x64両アーキテクチャのビルド・`work/` へのデプロイまで自動で行う。

```bat
build.bat
```

### デプロイ結果

`work/` にソースツリーと同じ構造でexe・pdb・exploit.pyが集約される。バイナリはアーキテクチャサフィックス（`-x86` / `-x64`）付きで配置される。

```
work/
├── exploitation/
│   └── 01_stack_overflow/
│       └── basic_ret_overwrite/
│           ├── basic_ret_overwrite-x86.exe
│           ├── basic_ret_overwrite-x86.pdb
│           └── exploit.py
└── internals/
    └── resolve_func_from_peb/
        ├── resolve_func_from_peb-x86.exe
        ├── resolve_func_from_peb-x64.exe
        └── resolve_func_from_peb.pdb
```

プロジェクトごとに対応アーキテクチャが異なる場合がある（`CMakeLists.txt` の `require_arch()` で制御）。

## エクスプロイトの実行

VMからネットワーク共有経由で `work/` 以下の `exploit.py` を実行する。WinDbgが自動的に起動する。

```powershell
python \\<host>\...\work\exploitation\01_stack_overflow\basic_ret_overwrite\exploit.py
```
