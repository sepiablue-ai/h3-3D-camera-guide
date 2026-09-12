# MiniMax H3 接続 / MiniMax H3 integration

## ガイド単体とH3の違い / Guide node versus H3

**日本語:** ガイド単体はこのノードとComfyUI標準Save Videoだけで動きます。[H3統合テンプレート](../workflows/minimax_h3_ref2va.json) は、別途H3を動かせる環境が必要です。このリポジトリはモデルや追加カスタムノードをインストールしません。

**English:** The guide-only workflow needs this node and ComfyUI's standard Save Video. The [H3 template](../workflows/minimax_h3_ref2va.json) additionally requires an H3-capable environment. This repository does not install model weights or other custom nodes.

## 必要ノード / Required nodes

| ノード / Node | 検証環境での提供元 / Provider in the tested environment |
|---|---|
| `H3CameraGuide` | このリポジトリ / This repository |
| `MiniMaxH3ReferenceToVideo`, `MiniMaxH3SigmaShift` | ComfyUI `comfy_extras.nodes_minimax_h3` |
| `MiniMaxChunkFeedForward` | ComfyUI-KJNodes |
| `H3SLAAttention` | ComfyUI-PlagueKind-Nodes |
| Loaders, sampler, VAE decode, Create Video, Save Video | ComfyUI |

**日本語:** これは検証時の提供元一覧であり、すべてのバージョンとの互換性を保証するものではありません。ノードが不足する場合は、ご自身のComfyUI環境で対応する提供元・バージョンを確認してください。使用する量子化モデル形式の対応も必要です。

**English:** These are the providers observed during validation, not a compatibility guarantee for every version. If a node is missing, check its provider/version in your installation. Your environment must also support the specified quantized model formats.

## テンプレートのモデル / Model filenames in the template

| Loader | Filename |
|---|---|
| UNETLoader | `minimax_h3_fused_refdelta_r1024_turbo8_mystic07_int8_convrot.safetensors` |
| CLIPLoader | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` |
| Video VAELoader | `minimax_h3_video_vae_int8_convrot.safetensors` |
| Audio VAELoader | `minimax_h3_audio_vae_fp32.safetensors` |

**日本語:** 上記は既存の検証環境で使用したファイル名です。モデルは同梱せず、ダウンロード可能性や利用許諾を保証しません。自分の環境で入手・使用する権利のある互換モデルを選択してください。モデルを変更した場合は結果も変わり得ます。

**English:** These are the filenames used in the existing validation environment. Models are not included; their availability or usage permissions are not guaranteed here. Select compatible models that you are entitled to obtain and use. Changing models may change results.

## 接続と初期設定 / Connections and defaults

```text
H3 3D Camera Guide.rgb_frames ──> MiniMaxH3ReferenceToVideo.ref_videos.ref_video_0
H3 3D Camera Guide.video ───────> Save Video (RGB Camera Guide)
Load Image × 3 ────────────────> MiniMaxH3ReferenceToVideo.ref_images.*
```

**日本語:** 「RGB Camera Guide」は保存用ノードで、その出力端子はH3へ接続しません。画像バッチを3DカメラノードからH3へ直接渡します。保存済みガイドを再利用する場合は、Load Video → Get Video Componentsのimages出力をH3へ接続してください。

**English:** “RGB Camera Guide” is a save node; its output is not connected to H3. The image batch goes directly from the 3D camera node to H3. To reuse a saved guide, connect Load Video → Get Video Components → images to H3 instead.

**日本語:** 初期値は576×1024、124フレーム、24fps、seed 42固定、res_multistep/simpleの4stepです。画像3枚は同一人物の参照へ差し替えてください。ガイド側の寸法・長さを変えたら、H3側のwidth/height/lengthも手動で合わせます。H3動画参照は24fpsで扱われます。検証した実装は17n+5フレームに切り詰め、124はその条件を満たします。

**English:** Defaults are 576×1024, 124 frames, 24 fps, fixed seed 42 and res_multistep/simple with four steps. Replace the three placeholder images with references of the same character. If you change guide dimensions/duration, manually match H3's width/height/length. H3 interprets the reference at 24 fps. The tested implementation truncates to 17n+5 frames; 124 satisfies that condition.

## 固定プロンプト / Fixed prompt

**日本語:** 「参照動画のカメラ・被写体の動き、構図、距離、タイミングに従う」と指示しています。人物の外観は画像参照から取り、棒人間の見た目は転写しないよう指定しています。軌道の時刻や角度をpromptへ手入力する必要はありません。現在のガイドの人型は固定ポーズです。

**English:** The prompt instructs H3 to follow the reference video's camera/subject motion, framing, distance and timing, while taking appearance from the image references and not copying the mannequin's appearance. There is no need to enter trajectory times or angles in the prompt. The current guide mannequin has a fixed pose.

**日本語:** 固定prompt版はworkflowの読み込み・接続を確認済みですが、このpromptでの追加生成は行っていません。過去の明示的な軌道promptによる比較結果とは区別してください。Ref2VAによる厳密なカメラ追従や一般的な成功率は未確認です。

**English:** Loading and wiring of the fixed-prompt workflow have been verified, but no additional generation was performed with that prompt. Keep this separate from the earlier explicit-trajectory-prompt comparison. Exact camera following and general success rates are not established.

## ライセンス / Licensing

**日本語:** 本体のMITライセンスは、上記の外部モデル・カスタムノード・参照画像の利用許諾を代わりに提供するものではありません。[第三者の権利表示](../THIRD_PARTY_NOTICES.md) を参照してください。

**English:** The project's MIT license does not grant permissions for external models, custom nodes or reference images. See [third-party notices](../THIRD_PARTY_NOTICES.md).
