# Superseded training attempt

The first attempt incorrectly cast cached FP32 backbone outputs to BF16 in the
head batch builder. Full Laya inference retains these outputs in FP32 inside its
mixed-precision pipeline. The final cache/full-inference verification rejected
the attempt. Do not use its head checkpoints or evaluation outputs.

The GPU-generated `features.pt` cache preserves the original FP32 outputs and is
valid for reuse. The corrected experiment is in `../laya_run_v2/`; it restarts
training from the original Laya decision layers with unchanged data,
hyperparameters, and validation-only checkpoint selection.
