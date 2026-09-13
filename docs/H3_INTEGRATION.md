# MiniMax H3 接続 / MiniMax H3 integration

## ルールベースのカメラ文 / Rule-based camera text

追加ノード `H3CameraPrompt` で、ガイドの `camera_json` とユーザーの場面・動作文を合成できます。人物の動作をカメラ文に混ぜず、全キー区間の周回・上下移動・距離・FOV・注視点の変化を記述します。`combined_prompt` をRef2VAへ接続してください。

`H3CameraPrompt` combines guide camera JSON with user-authored scene/action text. It describes every key interval's orbit, elevation, distance, FOV and aim changes without adding character actions. Connect `combined_prompt` to Ref2VA.

- 動画併用 / Video plus text: [minimax_h3_ref2va.json](../workflows/minimax_h3_ref2va.json)
- 動画なし / Camera text without guide video: [minimax_h3_camera_prompt_only.json](../workflows/minimax_h3_camera_prompt_only.json)

両方とも参照画像は使います。「動画なし」はT2VAへの変更ではなく、Ref2VAの動画参照だけを外した比較です。

Both workflows still use identity pictures. “Without video” removes only the guide-video reference; it does not switch the model to T2VA.

## 初期のカフェ着座比較 / Initial seated cafe comparison

同じseed 42、参照画像3枚、576×1024、124フレーム/24fps、既存Fused Ref2VA 4ステップ・SLA構成で各1本生成。場面文・軌道・人物指定は共通。動画入力と、それに対応するVideoラベルの説明だけを変更しました。

One clip per mode, with seed 42, the same three identity images, 576×1024, 124 frames at 24fps, and the existing fused Ref2VA four-step SLA setup. Scene, trajectory and identity instructions were shared. Only video conditioning and its corresponding reference-label clauses differed.

| 条件 / Mode | ComfyUI実行時間 / Execution | サンプルフレームでの観察 / Sampled-frame observation |
|---|---:|---|
| カメラ文のみ / Camera text only | 219.73 s | 俯瞰→正面→横、着座してカップを口へ運ぶ / Overhead to frontal to side; seated cup-to-mouth action |
| カメラ文＋動画 / Camera text + guide video | 235.00 s | 俯瞰→正面→横、着座してカップを口へ運ぶ / Overhead to frontal to side; seated cup-to-mouth action |

両方で1秒時点はまだ上方からの視点、2.5秒時点では正面でした。指定の「1秒で正面」は未達です。今回のseedでは動画なしでも順序は表現できましたが、動画参照の一般的な要否・優劣や角度精度はこの2本だけでは決められません。上記は目視観察であり、3Dカメラ姿勢の復元計測やユーザー評価ではありません。動画と音声は全デコード検査済みです。

Both remained above the subject at 1s and were frontal by 2.5s, missing the requested one-second arrival. This seed worked without video conditioning, but two clips do not establish a general winner or angular accuracy. Observations are qualitative, not recovered camera measurements or user ratings. Video and audio passed full decoding.


---

以下には現在の導入情報と、明示した旧固定プロンプトの検証履歴を分けて記載します。公開チュートリアル末尾のカフェ例は別の後続実験です。[動画の条件](media/README.md)を参照してください。

The sections below include current setup information and explicitly labeled historical fixed-prompt tests. The cafe clip at the end of the public tutorial comes from a separate later experiment; see [video conditions](media/README.md).


## ガイド単体とH3の違い / Guide node versus H3

**日本語:** ガイド単体はこのノードとComfyUI標準Save Videoだけで動きます。[H3統合テンプレート](../workflows/minimax_h3_ref2va.json) は、別途H3を動かせる環境が必要です。このリポジトリはモデルや追加カスタムノードをインストールしません。

**English:** The guide-only workflow needs this node and ComfyUI's standard Save Video. The [H3 template](../workflows/minimax_h3_ref2va.json) additionally requires an H3-capable environment. This repository does not install model weights or other custom nodes.

## 必要ノード / Required nodes

| ノード / Node | 検証環境での提供元 / Provider in the tested environment |
|---|---|
| `H3CameraGuide`, `H3CameraPrompt` | このリポジトリ / This repository |
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
H3 3D Camera Guide.camera_json ─> H3CameraPrompt.camera_json
H3CameraPrompt.combined_prompt ─> MiniMaxH3ReferenceToVideo.prompt
H3 3D Camera Guide.rgb_frames ──> MiniMaxH3ReferenceToVideo.ref_videos.ref_video_0
H3 3D Camera Guide.video ───────> Save Video (RGB Camera Guide)
Load Image × 3 ────────────────> MiniMaxH3ReferenceToVideo.ref_images.*
```

**日本語:** 「RGB Camera Guide」は保存用ノードで、その出力端子はH3へ接続しません。画像バッチを3DカメラノードからH3へ直接渡します。保存済みガイドは、3D Camera Guideのsource_modeをreuse_videoにし、video_pathにパスを指定すると同じ接続のまま再利用できます。Load VideoのVIDEOをexisting_videoへ接続する方法もあります。

**English:** “RGB Camera Guide” is a save node; its output is not connected to H3. The image batch goes directly from the 3D camera node to H3. To reuse a saved guide with the same wiring, select reuse_video on the 3D Camera Guide node and set video_path. Alternatively, connect a Load Video VIDEO output to existing_video.

**日本語:** 初期値は576×1024、124フレーム、24fps、seed 42固定、res_multistep/simpleの4stepです。画像3枚は同一人物の参照へ差し替えてください。ガイド側の寸法・長さを変えたら、H3側のwidth/height/lengthも手動で合わせます。H3動画参照は24fpsで扱われます。検証した実装は17n+5フレームに切り詰め、124はその条件を満たします。

**English:** Defaults are 576×1024, 124 frames, 24 fps, fixed seed 42 and res_multistep/simple with four steps. Replace the three placeholder images with references of the same character. If you change guide dimensions/duration, manually match H3's width/height/length. H3 interprets the reference at 24 fps. The tested implementation truncates to 17n+5 frames; 124 satisfies that condition.

## 旧固定プロンプト（現行テンプレートとは異なる） / Historical fixed prompt (not the current template)

**日本語:** 「参照動画のカメラの動き、構図、距離、タイミングだけに従う」と指示しています。人物の外観は画像参照から取り、棒人間の見た目は転写しないよう指定しています。軌道の時刻や角度をpromptへ手入力する必要はありません。人物の姿勢・動作は本文から指定します。固定ポーズの人型と「座る」などを競合させないため、ガイドの姿勢は転写しない指示に変更しました。

**English:** The prompt instructs H3 to follow the reference video's camera motion only, framing, distance and timing, while taking appearance from the image references and not copying the mannequin's appearance. There is no need to enter trajectory times or angles in the prompt. Subject pose and action come from the scene text; the guide proxy pose is explicitly excluded to avoid conflicts such as standing versus sitting.

## 旧カフェ座位の追従検証 / Seated cafe validation (2026-09-12)

**日本語:** 「座ってコーヒーを飲む」場面で4条件を各1本実生成しました。4本は同一のカメラ専用の固定prompt・seed 42・参照画像3枚・モデル・576×1024/124f/24fps・4stepを使用。軌道の時刻や角度はpromptに記述していません。下表は抽出フレームの定性的な観察であり、復元カメラ角度の測定やユーザーによる品質評価ではありません。

**English:** Generated one video for each of four seated coffee-drinking conditions. All four used the same camera-only fixed prompt, seed 42, three image references, model, 576×1024/124f/24fps and four steps. The prompt contains no trajectory angles or times. The table reports qualitative frame inspection, not recovered camera-angle measurements or user quality ratings.

| 条件 / Condition | 変更 / Change | 観察 / Observation | 実行時間 / Wall time |
|---|---|---|---|
| A | 既存人型動画＋カメラ専用prompt / Original mannequin clip + camera-only prompt | 元の結果より横の視点変化が明確。天井視点なし / Clearer lateral change than original; no overhead opening | 230.29 s |
| B | Aの人型を球へ / Replace mannequin with ball | Aより横の変化が弱い。天井視点なし / Weaker lateral change than A; no overhead opening | 230.33 s |
| C | Bに床の4色の目印 / Add four colored floor cues to B | Bより横の変化が明確。天井視点なし / Clearer lateral change than B; no overhead opening | 225.31 s |
| D | Cの降下を1秒から2.5秒へ / Extend C descent from 1 to 2.5 s | 天井視点は改善せず。横の変化は残る / Overhead opening still absent; lateral change remains | 230.27 s |

**日本語:** 人型の立ち姿を転写する指定と「座る」は文章上で競合していました。その指定を除き、人物の動作は本文、カメラは動画から取るよう修正しました。ただし、球への変更・今回の床模様・降下の低速化では天井視点を回復できず、3仮説のいずれかを唯一の原因と断定できません。改善済みなのは参照の役割分担と一部の横方向の動きで、天井→正面の追従は未解決です。

**English:** Transferring the standing proxy pose conflicts with the seated action in the text. The revised prompt takes action from text and camera movement from video. However, replacing the proxy, adding these floor cues and slowing the descent did not recover the overhead opening. None of the three hypotheses is established as the sole cause. Reference roles and some lateral motion improved; overhead-to-front tracking remains unresolved.

**日本語:** 実装上、H3のVAEには全124フレーム、Qwenには2fpsで抽出した11フレームが渡ります。「H3が2fpsしか見ない」わけではありません。配線不良やガイド未入力は確認されませんでした。全条件でSLA sparsity 0.9 / reference_protection Offを維持しました。この参照保護設定の影響は未検証の別候補であり、今回の原因と断定したり、無検証で設定を変更したりしていません。

**English:** The inspected H3 implementation feeds all 124 frames to the VAE and 11 frames sampled at 2 fps to Qwen. H3 does not receive only 2 fps overall. No missing guide connection was found. All conditions retained SLA sparsity 0.9 / reference_protection Off. The effect of reference protection remains an untested candidate, not an established cause or an unvalidated workflow change.

**日本語:** 単一seedの観察です。元のユーザー生成は生のRGB、Aは保存済みMP4の再読み込みなので、元結果とAは厳密なpromptのみの比較ではありません。球はシルエット・画面占有率も変えます。Dは全長を固定したため、後半の周回時間も短くなっています。生成4本と入力ガイドは全フレームをデコード検証済みです。入力動画は再描画せず、球のガイド3本は各16〜17秒で一度だけ作成しました。個人用画像・動画・実行記録は配布物に含めません。

**English:** This is a single-seed observation. The original user run consumed raw RGB while A loaded a saved MP4, so that comparison is not a strict prompt-only ablation. A ball also changes silhouette and screen coverage. D keeps total duration fixed and therefore shortens the later orbit. All four outputs and input guides passed complete decoding. H3 reused the input clips without rerendering; the three ball guides were rendered once, taking 16–17 seconds each. Personal images, videos and raw receipts are excluded from distribution.

## ライセンス / Licensing

**日本語:** 本体のMITライセンスは、上記の外部モデル・カスタムノード・参照画像の利用許諾を代わりに提供するものではありません。[第三者の権利表示](../THIRD_PARTY_NOTICES.md) を参照してください。

**English:** The project's MIT license does not grant permissions for external models, custom nodes or reference images. See [third-party notices](../THIRD_PARTY_NOTICES.md).
