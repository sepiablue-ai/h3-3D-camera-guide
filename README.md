# H3 3D Camera Guide for ComfyUI

**日本語:** ノード内の3Dビューでカメラを動かし、キーフレームから簡易人型のRGBガイド動画を作る、ローカル完結のComfyUIカスタムノードです。MiniMax H3 Ref2VAへ参照動画として接続できます。

**English:** A local ComfyUI custom node for editing camera motion in an embedded 3D view and rendering RGB guide videos of a simple mannequin from keyframes. Its frames can be connected to MiniMax H3 Ref2VA as a video reference.

## 機能 / Features

| 日本語 | English |
|---|---|
| Three.js編集ビューと出力構図プレビュー | Three.js editor and output-camera framing preview |
| XYZドラッグ、Orbit・Elevation・Distance・FOV・注視点の調整 | XYZ dragging; orbit, elevation, distance, FOV and target controls |
| タイムライン、キー保存、再生、一時停止、停止、スクラブ | Timeline, keyframes, playback, pause, stop and scrubbing |
| workflowにカメラ軌道を保存・復元 | Camera state persists in saved workflows |
| 人型と無地の床だけのRGBフレーム列・VIDEO出力 | RGB frame batches and VIDEO containing only the mannequin and plain floor |
| 編集用カメラ・軌道・グリッド・軸・UIは出力に含まない | Editor cameras, paths, grids, axes and UI are excluded from renders |
| Three.js同梱、実行時CDN不要、追加Pythonパッケージ不要 | Vendored Three.js; no runtime CDN or additional Python packages |

## 必要環境 / Requirements

**日本語:** ComfyUIの `comfy_api.latest.InputImpl.VideoFromComponents` と標準Save Videoを使用します。動作確認環境はWindows 11、ComfyUI 0.34.0、frontend 1.51.9、Python 3.13です。古いComfyUIや他OSでの動作は未検証です。ブラウザの3D表示にはWebGLが必要です。RGB出力はCPU処理で、ガイドノード自体にCUDA GPUやH3モデルは不要です。

**English:** Requires ComfyUI's `comfy_api.latest.InputImpl.VideoFromComponents` and standard Save Video node. Tested on Windows 11, ComfyUI 0.34.0, frontend 1.51.9 and Python 3.13. Older ComfyUI versions and other operating systems are untested. The browser editor requires WebGL. RGB rendering runs on the CPU; the guide node itself does not require a CUDA GPU or H3 model.

## インストール / Installation

1. **日本語:** このリポジトリをダウンロードし、フォルダを `ComfyUI/custom_nodes/h3-3D-camera-guide` に配置します。ZIPの場合は二重フォルダにならないようにしてください。
   **English:** Download this repository and place it at `ComfyUI/custom_nodes/h3-3D-camera-guide`. When extracting a ZIP, avoid an extra nested folder.
2. **日本語:** ComfyUIを再起動し、ブラウザを再読み込みします。
   **English:** Restart ComfyUI and reload its browser page.
3. **日本語:** ノード検索で **H3 3D Camera Guide** を追加するか、下記のサンプルを読み込みます。カテゴリは `H3/Camera Guide` です。
   **English:** Add **H3 3D Camera Guide** from node search or load a sample below. The category is `H3/Camera Guide`.

**日本語:** `requirements.txt` は追加依存がないことを示すコメントのみです。通常利用でpipやnpmによるインストール、ビルドは不要です。

**English:** `requirements.txt` contains only a note that there are no extra dependencies. Normal use requires no pip/npm installation or build step.

## サンプルworkflow / Sample workflows

| ファイル / File | 用途 / Purpose |
|---|---|
| [camera_guide.json](workflows/camera_guide.json) | ガイド生成→保存の2ノード / Two nodes: render and save a guide |
| [camera_guide.api.json](workflows/camera_guide.api.json) | 同じ構成のAPI形式 / API-format equivalent |
| [minimax_h3_ref2va.json](workflows/minimax_h3_ref2va.json) | 3Dカメラ→H3 Ref2VA→動画保存 / Integrated camera-to-H3 workflow |

**日本語:** 最初はガイド単体のworkflowを使ってください。H3統合版は追加ノードとモデルが必要なテンプレートです。3つのLoad Imageで、自分の同一人物の参照画像を選択してください。`reference_1.png`〜`reference_3.png` は差し替え用の名前で、画像は同梱しません。使用モデルと追加ノードは [H3接続説明](docs/H3_INTEGRATION.md) に記載しています。

**English:** Start with the guide-only workflow. The H3 workflow is a template requiring additional nodes and models. Select your own reference images of the same character in its three Load Image nodes. `reference_1.png` through `reference_3.png` are placeholder filenames; images are not included. See [H3 integration](docs/H3_INTEGRATION.md) for required nodes and model filenames.

## 操作 / Controls

1. **日本語:** 左が編集ビュー、右が出力カメラのプレビューです。左の空白ドラッグで編集視点を回転し、ホイールで拡大縮小します。
   **English:** The left view is the editor; the right shows output-camera framing. Drag empty space to orbit the editor view; use the wheel to zoom.
2. **日本語:** カメラのXYZ矢印をドラッグするか、各数値を調整します。編集視点を動かすだけでは出力カメラは変わりません。
   **English:** Drag the camera's XYZ arrows or adjust its values. Moving the editor view alone does not change the output camera.
3. **日本語:** 時刻を選び、カメラを配置して **キー保存 / 更新** を押します。同時刻のキーは上書き、新時刻なら追加します。未保存の変更は動画へ反映されません。
   **English:** Select a time, position the camera, and click **キー保存 / 更新** (save/update key). This updates an existing key or adds a new one. Unsaved edits do not affect the rendered video.
4. **日本語:** 再生・停止・タイムラインで動きを確認します。**天井 → 正面 → 右へ** は初期プリセットです。UIのボタン名は現在日本語です。
   **English:** Preview motion with playback, stop and the timeline. **天井 → 正面 → 右へ** resets the overhead-to-front-to-side preset. Editor button labels are currently Japanese.
5. **日本語:** ComfyUIのworkflowを保存すると、軌道も保存されます。iframe内で操作した後はノードタイトルをクリックし、`Ctrl+S` を押します。
   **English:** Saving the ComfyUI workflow also saves the trajectory. After interacting inside the iframe, click the node title before pressing `Ctrl+S`.
6. **日本語:** ComfyUIの実行ボタンを押すと、保存済みキーからRGB動画を生成します。
   **English:** Run the workflow to render RGB video from the saved keys.

## 出力と接続 / Outputs and connections

| 出力 / Output | 型 / Type | 用途 / Use |
|---|---|---|
| `rgb_frames` | IMAGE | H3の参照動画入力、画像プリプロセッサ / H3 reference-video input or image preprocessors |
| `video` | VIDEO | 標準Save Videoへ接続 / Connect to standard Save Video |
| `fps` | FLOAT | フレームレート / Frame rate |
| `camera_json` | STRING | 保存されたキーのJSON / Serialized camera keyframes |

**日本語:** H3へは `rgb_frames` → `ref_videos.ref_video_0` を接続し、ガイドを **24fps** にします。統合workflowの「RGB Camera Guide」は確認用動画を保存するSave Videoです。その出力が未接続でも正常です。H3へは3Dカメラノードから直接フレーム列を渡しています。

**English:** Connect `rgb_frames` to H3's `ref_videos.ref_video_0` and use **24 fps**. The integrated workflow's “RGB Camera Guide” node is a Save Video node for the guide preview. Its output may remain unconnected; H3 receives frames directly from the 3D camera node.

**日本語:** H3テンプレートのpromptは「参照動画のカメラ・被写体の動きに従う」という固定指示です。軌道を変更するたびに時刻・角度・移動方向を書き直す必要はありません。人物や画風を変えたい場合は、その部分のpromptを調整してください。

**English:** The H3 template uses a fixed instruction to follow the reference video's camera and subject motion. Changing the trajectory does not require rewriting timestamps, angles or directions. Adjust the identity/style instructions if you want a different subject or appearance.

## 仕様と制限 / Behavior and limitations

| 日本語 | English |
|---|---|
| Y上、+Z正面。Orbit 0°は正面、+90°は+X側 | Y up, +Z front. Orbit 0° is front; +90° moves to the +X side |
| 注視点を中心に球面座標で移動。独立rollなし | Spherical motion around a target; no independent roll |
| smoothstep補間。各キーで速度が0になる | Smoothstep interpolation, with zero velocity at each key |
| 連続角度。350→370は20°、350→10は逆方向340° | Unwrapped angles: 350→370 is +20°; 350→10 is −340° |
| 124f/24fpsは約5.167秒、最終フレーム時刻は5.125秒 | 124 frames at 24 fps last about 5.167 s; last frame timestamp is 5.125 s |
| キーは1〜200個、時刻0〜120秒。範囲外のキーは出力に到達しない | 1–200 keys at 0–120 s. Keys beyond the output duration are not reached |
| fps・frames変更時はキー時刻も確認。自動フレーミングなし | Check key times after changing fps/frame count. No automatic framing |
| プレビューと出力は同じ形状・カメラ式。照明・色・AAは異なる | Preview and render share geometry/camera math; lighting, color and AA differ |
| CPUレンダラーはRAMと時間を使用。1.8億画素上限、RGBテンソルだけで最大約2.16GB | CPU rendering takes time and RAM. Limit: 180 million pixels, up to ~2.16 GB for the RGB tensor alone |
| 人型は固定ポーズ。Depth / Edge / Pose専用出力は未実装 | Mannequin has a fixed pose. Dedicated depth/edge/pose outputs are not implemented |
| ControlNet実生成は未検証。RGBをdepth/pose条件と同一視しない | ControlNet generation is untested. RGB is not a depth/pose condition by itself |
| Ref2VAはガイドへの厳密な追従を保証しない | Ref2VA does not guarantee exact trajectory following |

## 検証状況 / Validation status

**日本語:** 実画面でXYZドラッグ、再生・スクラブ、キー編集、workflow保存・再読み込み、Save Video出力を確認済みです。JavaScript/Pythonのカメラ式一致を含む5件のテストが成功しました。過去の同一seed・prompt・参照画像によるH3各1本の比較では、初期視点と降下タイミングに部分的な改善を観察しましたが、厳密な軌道一致は未達でした。その比較は時刻・角度を記述した旧promptで行ったもので、今回同梱する固定promptの品質検証ではありません。検証用の人物画像・動画・ログは公開配布物に含めません。

**English:** Verified in the actual UI: XYZ dragging, playback/scrubbing, key editing, save/reload, and Save Video output. Five tests passed, including JavaScript/Python camera-math parity. An earlier single-seed H3 comparison with equal prompts and image references showed partial improvement in initial viewpoint and descent timing, but not exact trajectory following. That comparison used an older prompt containing explicit times and angles; it does not establish quality for the fixed prompt shipped here. Personal reference images, videos and raw logs are not part of the public distribution.

## フォルダ構成 / Repository layout

```text
h3-3D-camera-guide/
├── __init__.py, nodes.py, camera.py, renderer.py  # Python runtime
├── web/                                         # Editor and vendored Three.js
├── workflows/                                   # Public example workflows
├── tests/                                       # Camera/render tests
├── tools/                                       # Optional developer tools
├── docs/H3_INTEGRATION.md                        # H3 setup (JA / EN)
├── LICENSE                                      # Project MIT license
├── THIRD_PARTY_NOTICES.md                        # Third-party notices (JA / EN)
└── README.md
```

**日本語:** 手元の `validation/` と直下の `MiniMax_H3_3D_Camera_Guide.json` は個人用としてGit対象外です。公開用H3テンプレートは `workflows/` にあります。通常利用に `tests/` と `tools/` は不要です。

**English:** Local `validation/` and the root-level `MiniMax_H3_3D_Camera_Guide.json` are excluded from Git as private working files. The public H3 template lives in `workflows/`. `tests/` and `tools/` are not required at runtime.

## 開発 / Development

**日本語:** リポジトリ直下でComfyUIのPythonを使ってテストします。JS/Python一致テストにはNode.jsが必要です。`check_release.py` は配布ファイル、ローカルリンク、workflow接続、同梱ハッシュを確認します。H3生成は実行しません。

**English:** Run tests from the repository root using ComfyUI's Python. Node.js is needed for the JS/Python parity test. `check_release.py` checks release files, local documentation links, workflow connections and vendor hashes. It does not run H3 generation.

```powershell
python -s tests/test_camera.py
python -s tools/check_release.py
```

**日本語:** Windows開発用ジャンクションは、ComfyUIフォルダを明示して作成できます。既存の登録先は上書きしません。

**English:** For Windows development, create a junction by explicitly specifying the ComfyUI folder. Existing destinations are not overwritten.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/install.ps1 -ComfyRoot 'D:\ComfyUI_windows_portable\ComfyUI'
```

**日本語:** `tools/fetch_vendor.py` はThree.js r169を上流から再取得する開発専用ツールで、ネット接続が必要です。通常利用では実行しません。

**English:** `tools/fetch_vendor.py` is a development-only tool for fetching Three.js r169 from upstream and requires network access. Do not run it for normal installation.

## ライセンス / License

**日本語:** 本体の独自コード・ドキュメント・独自workflow構成は [MIT](LICENSE)。Three.jsの著作権表示・MIT原文は [別途保持](web/vendor/THREE-LICENSE.txt) しています。モデルや参照画像、生成物を本体のMITで一括許諾するものではありません。詳細は [第三者の権利表示](THIRD_PARTY_NOTICES.md) を参照してください。

**English:** Original project code, documentation and workflow configuration are licensed under [MIT](LICENSE). Three.js retains its [own copyright notice and MIT text](web/vendor/THREE-LICENSE.txt). This does not license model weights, reference assets or generated media collectively under the project's MIT license. See [third-party notices](THIRD_PARTY_NOTICES.md).
