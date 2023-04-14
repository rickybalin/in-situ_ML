# Create a TorchScript version of the ResNet50 model

import torch
import torchvision
from time import perf_counter

device = 'cpu'

model = torchvision.models.resnet50()
model.eval()
#model.to(device)

#dummy_input = torch.rand(1, 3, 224, 224i, device=device)
dummy_input = torch.rand(1, 3, 224, 224)

model_jit = torch.jit.trace(model, dummy_input)
tic = perf_counter()
predictions = model_jit(dummy_input)
toc = perf_counter()
print(f"Inference time: {toc-tic}")

torch.jit.save(model_jit, f"resnet50_jit.pt")


