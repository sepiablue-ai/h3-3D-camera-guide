# 第三者のコードと権利 / Third-party notices

## Three.js r169

| 項目 / Item | 内容 / Details |
|---|---|
| Upstream | [mrdoob/three.js, r169](https://github.com/mrdoob/three.js/tree/r169) |
| Copyright | Copyright © 2010-2024 three.js authors |
| License | MIT — [同梱する原文 / bundled original](web/vendor/THREE-LICENSE.txt) |
| Files | `web/vendor/three.module.mjs`, `OrbitControls.mjs`, `TransformControls.mjs` |
| Provenance | [取得元・SHA-256 / source URLs and SHA-256](web/vendor/manifest.json) |

**日本語:** Three.js本体とコントロールを同梱しています。ComfyUIによる拡張スクリプトの自動読み込みを避けるため、拡張子を `.js` から `.mjs` に変更しています。コントロール2ファイルの `three` インポートは `./three.module.mjs` へ変更しています。改行・UTF-8エンコーディングの差が含まれる場合があります。Three.jsの著作権表示とMITライセンス原文は保持しています。

**English:** This repository vendors Three.js and its controls. Files are renamed from `.js` to `.mjs` to avoid ComfyUI automatically loading them as extensions. The controls' `three` imports are rewritten to `./three.module.mjs`. Line-ending and UTF-8 encoding differences may also be present. The upstream copyright notice and original MIT license are retained.

## 本体と外部アセット / Project and external assets

**日本語:** [LICENSE](LICENSE) は、このプロジェクトの独自コード・ドキュメント・独自のworkflow構成へのMITライセンスです。第三者コードには上記の権利表示が適用されます。workflow内で指定するモデル名はモデルの同梱や権利の譲渡を意味しません。ComfyUI、追加カスタムノード、モデル重み、利用者の参照画像・音声・動画、生成物の利用条件は、それぞれのライセンスや権利に従ってください。本体のMITライセンスでそれらを一括許諾するものではありません。

**English:** [LICENSE](LICENSE) applies to this project's original code, documentation, and original workflow configuration. Third-party code retains the notices above. Model filenames in a workflow do not distribute those weights or grant rights to them. ComfyUI, additional custom nodes, model weights, users' reference images/audio/video, and generated media remain subject to their applicable licenses and rights; this project's MIT license does not license them collectively.

## 設計上の参考 / Design references

- [ComfyUI-qwenmultiangle](https://github.com/jtydhr88/ComfyUI-qwenmultiangle)
- [ComfyUI-3D-motion-reference](https://github.com/arturitu/ComfyUI-3D-motion-reference)
- [ComfyUI-scene-camera-action](https://github.com/arturitu/ComfyUI-scene-camera-action)
- [comfyblockout](https://github.com/spiritform/comfyblockout)

**日本語:** これらはUIや接続方式の設計上の参考です。これらのリポジトリのソースファイルは本配布物にコピーしていません。上記のThree.jsは別途その上流から取得しています。

**English:** These projects informed the UI and integration design. Their source files are not copied into this distribution. The vendored Three.js files were obtained separately from their own upstream.
