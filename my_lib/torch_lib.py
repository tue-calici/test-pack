import torch

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def tensor_wrap(data, device=None) -> torch.Tensor:
    if device is None:
        device = DEVICE
    return torch.tensor(data, device=device)
