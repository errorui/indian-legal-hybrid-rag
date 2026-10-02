# Laya frozen-backbone training results

GPU: NVIDIA GeForce RTX 3050 Laptop GPU. Train: 160; validation: 40; evaluation: 100.

Trained 26,245,121 parameters in the two decision layers and scorer; froze 395,048,706 parameters.
Selected epoch 10 by validation loss; threshold stayed 0.5.

| Model | Overall | Single-turn | Multi-turn | Missed search / 50 | Extra search / 50 | Median ms |
|---|---:|---:|---:|---:|---:|---:|
| Laya before | 52% | 48% | 56% | 45 | 3 | 32.1 |
| Laya fine-tuned | 70% | 92% | 48% | 11 | 19 | 31.4 |

Training peak allocated VRAM: 639.7 MiB. Last invocation: 24.8 seconds.

Validation accuracy: 55.0%; selected by validation loss, not evaluation accuracy.

The overall gain is driven by single-turn cases. Multi-turn accuracy regressed and extra searches increased; this checkpoint remains a pilot.

Frozen weights were hash-checked unchanged; no backbone gradients; all histories fit; cached/full inference agreed.

This run does not change the production router or the original model snapshot. Restore the pinned original Laya model, then load head_epoch_10.safetensors and the validation temperature for this checkpoint.

Small constructed training pilot; existing evaluation repeatedly inspected; no fresh production test.
