"""Minimal vision service using torchvision pretrained model for classification.
This is intentionally tiny: for real detection tasks use Detectron2/YOLO etc.
"""
from PIL import Image
import torch
import torchvision.transforms as T
from torchvision import models


# load a pretrained resnet18 for demo
_model = None
_transform = T.Compose([
                        T.Resize(256),
                        T.CenterCrop(224),
                        T.ToTensor(),
                        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
                        ])


LABELS = None




def init_model():
    global _model, LABELS
    if _model is None:
        _model = models.resnet18(pretrained=True)
        _model.eval()
    # load imagenet labels file if available
    try:
        LABELS = []
        with open('imagenet_labels.txt') as f:
            LABELS = [l.strip() for l in f.readlines()]
    except Exception:
        LABELS = [str(i) for i in range(1000)]




def classify_image(image_path: str, topk: int = 3):
    init_model()
    img = Image.open(image_path).convert('RGB')
    x = _transform(img).unsqueeze(0)
    with torch.no_grad():
        out = _model(x)
        probs = torch.nn.functional.softmax(out[0], dim=0)
        topk_vals, topk_idx = torch.topk(probs, topk)
        results = []
        for v, idx in zip(topk_vals.tolist(), topk_idx.tolist()):
            label = LABELS[idx] if LABELS else str(idx)
            results.append({"label": label, "score": v})
    return results
