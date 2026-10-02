import torch

from train_laya import batch, configure_model


def test_feature_batch_preserves_encoder_precision(monkeypatch):
    original_to = torch.Tensor.to

    def keep_cuda_transfer_on_cpu(self, *args, **kwargs):
        if args == ('cuda',) and not kwargs:
            return self
        return original_to(self, *args, **kwargs)

    monkeypatch.setattr(torch.Tensor, 'to', keep_cuda_transfer_on_cpu)
    # These values would silently change if a FP32 backbone output became BF16.
    features = torch.tensor([[1.001, 0.49999], [1.003, -0.50001]], dtype=torch.float32)
    h, mask, markers, targets = batch([dict(ids=[1, 2], features=features, markers=[0, 1], label=1)])
    assert h.dtype == features.dtype
    assert torch.equal(h[0], features)
    assert mask.all() and markers.tolist() == [[0, 1]] and targets.tolist() == [1]


def test_only_decision_layers_and_scorer_are_trainable():
    model = torch.nn.Module()
    model.encoder = torch.nn.Linear(4, 4)
    model.head = torch.nn.Sequential(torch.nn.Linear(4, 4))
    model.scorer = torch.nn.Linear(4, 1)
    model.type_emb = torch.nn.Embedding(3, 4)
    model.act_head = torch.nn.Linear(4, 2)
    configure_model(model)
    assert {n.split('.')[0] for n, p in model.named_parameters() if p.requires_grad} == {'head', 'scorer'}
    assert not model.encoder.training
    assert all(not p.requires_grad for p in model.encoder.parameters())
    assert all(not p.requires_grad for p in model.act_head.parameters())
