# 公開デモ動画 / Public tutorial media

[▶ 使い方動画を開く・ダウンロード / Watch or download the tutorial](camera-guide-tutorial.mp4)

| ファイル / File | 内容 / Contents |
|---|---|
| `camera-guide-tutorial.mp4` | 67秒、1920×1080、H.264、30fps、音声なし / 67 seconds, 1920×1080, H.264, 30 fps, silent |
| `tutorial-preview.jpg` | 動画から抽出したプレビュー画像 / Preview frame extracted from the tutorial |

## 内容と生成例の条件 / Contents and example conditions

**日本語:** 0〜57秒は実際のComfyUI操作画面です。カメラのドラッグ、数値調整、キー保存、再生・スクラブ、workflow保存、H3への配線とscene_promptを説明します。操作画面の連続キャプチャに拡大と字幕を加えています。収録頻度は約3〜10fpsで、30fpsの動画へ変換する際は同じ画面を保持しています。架空のUIや動きの補間映像ではありません。

**English:** Seconds 0–57 show actual ComfyUI interaction: camera dragging, numeric controls, saving keys, playback/scrubbing, workflow saving, H3 connections, and scene text. The edit adds zooms and captions to sequential screen captures. Screens were captured at approximately 3–10 fps and held as needed in the 30 fps export; the UI and its motion are not synthesized.

| 時間 / Time | 左 / Left | 右 / Right |
|---|---|---|
| 57–62 s | Hard軌道のRGBガイド / RGB guide for the Hard path | 草原で立つ2Dアニメ女性。カメラ文章＋参照動画 / Standing anime woman in grassland; camera text plus guide-video conditioning |
| 62–67 s | 同じHard軌道、比較用 / Same Hard path, for comparison | カフェで座ってコーヒーを飲む2Dアニメ女性。検証用の改善カメラ文章のみ / Seated anime woman drinking coffee; experimental improved camera text only |

**日本語:** 両方とも既存の生成動画を先頭から5秒使用しています。軌道は0秒でOrbit 0°・Elevation 85°・Distance 4、2.5秒で0°・0°・4、5.125秒で90°・0°・2.8、FOV 45°、注視点は(0, 1, 0)です。末尾のカフェ例は参照動画をH3へ入力していません。左の動画は目標との比較用です。

**English:** Both examples use the first five seconds of existing outputs. The path uses orbit/elevation/distance values of 0°/85°/4 at 0 s, 0°/0°/4 at 2.5 s, and 90°/0°/2.8 at 5.125 s, with a 45° FOV and target (0, 1, 0). The cafe example did not feed a guide video to H3; its left-hand clip visualizes the target for comparison.

**日本語:** カフェ例の投影方向を使う改善ルールは、ローカル検証後に公開カスタムノードへ統合しました。動画は統合前の既存生成結果です。配布workflowからこの結果がそのまま再現できるという意味ではありません。中間時刻の角度にはずれが残り、カメラ追従を保証するものでもありません。個人の参照画像、モデル、元の生成動画、実行ログ、録画素材は同梱していません。

**English:** The cafe clip uses projected-direction rules that were subsequently integrated into the released custom node. The video retains the existing output generated before integration. This is not an exact reproduction example for the distributed workflows. Intermediate camera angles still differ from the target, and tracking is not guaranteed. Personal reference images, weights, original generated clips, run logs, and raw recordings are not included.

## メディアの権利 / Media rights

**日本語:** このMP4とプレビュー画像は閲覧・紹介用のデモで、コード用の[MITライセンス](../../LICENSE)の対象外です。メディアに対する別途の再利用ライセンスは付与していません。画面に含まれるComfyUI等の第三者UI・名称、モデル由来の生成映像について、本プロジェクトが第三者の権利を一括許諾するものではありません。紹介時はこの動画またはリポジトリへのリンクを利用できます。

**English:** This MP4 and preview image are demonstration media for viewing and reference, excluded from the code's [MIT license](../../LICENSE). No separate media reuse license is granted. The project does not collectively license third-party UI/names, including ComfyUI, or rights associated with model-generated footage. You may link to the video or repository when introducing the project.

**日本語:** 通常のGitファイルとして管理しています。Git LFSや外部動画ホスティングは不要で、ノードの実行時にも読み込みません。

**English:** These are ordinary Git files. Git LFS and external video hosting are not required, and the node does not load this media at runtime.
