# 固定ページの保護（2026-10-29）

ニュース・コラム更新の本番生成では `static_guard.py` が `static-baseline.json` と照合します。固定ページ、既存の記事、画像、共通CSS/JSなど155ファイルを保護します。TOPはニュース枠だけを比較から除きます。ニュース・コラム一覧、サイトマップ、新規CMS記事とCMS画像は更新可能です。

差異があれば生成を失敗させ、GitHub Releaseの作成前に停止します。公開処理から基準ファイルを自動更新してはいけません。

## 固定ページを意図的に変更する場合

1. GitHub mainの最新のソースと直前の本番Releaseを取得する。
2. 対象ページだけ修正する。ページ固有のCSSは専用ファイルとし、共通ファイルを不要に変えない。
3. 本番形式で生成し、直前のReleaseと全ファイル比較する。他ページの変更がないことを確認する。
4. 承認された変更ファイルだけ、static_guard.digestで算出した値へ基準を更新する。全ファイルの無条件更新は禁止。
5. `python3 -m unittest discover -s cms/tests -v` を実行する。
6. GitHubの公開ワークフローでsourceにpublishedを指定して実行する。公開後も全HTMLと参照画像を確認する。

緊QRは marketing_pages.py → kinqr_page.py、専用スタイルは dist/assets/kinqr.css。共有site.css/site.jsは今回変更していません。

ローカルの古い一式や以前作成したZIPを再アップロードすると、この仕組みを経由せず上書きする可能性があります。次回の修正もGitHub mainを生成元として行ってください。
