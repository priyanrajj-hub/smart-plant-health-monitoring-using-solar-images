import torch
import torch.nn as nn
import torchvision.models as models

class CropDiseaseClassifier(nn.Module):
    def __init__(self, num_classes=30, use_ood=True):
        super(CropDiseaseClassifier, self).__init__()
        # Using a reliable lightweight backbone 
        self.backbone = models.efficientnet_b0(pretrained=True)
        num_ftrs = self.backbone.classifier[1].in_features
        self.backbone.classifier[1] = nn.Linear(num_ftrs, num_classes)
        self.use_ood = use_ood

    def forward(self, x):
        logits = self.backbone(x)
        return logits

def calculate_ood_score(logits, temperature=1.0):
    """
    Computes Energy Score for Out-of-Distribution detection.
    Lower energy score indicates higher confidence it belongs in-distribution.
    """
    energy = -temperature * torch.logsumexp(logits / temperature, dim=1)
    return energy

def calibration_temperature_scaling(logits, temperature_parameter):
    """ Post-hoc probability calibration scaling """
    return logits / temperature_parameter

def train_model(model, train_loader, optimizer, criterion, epochs=1):
    """
    Executes core training loop over the PyTorch dataloader.
    """
    model.train()
    for epoch in range(epochs):
        running_loss = 0.0
        for inputs, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        print(f"Epoch {epoch+1} completed. Loss: {running_loss/len(train_loader):.4f}")
    return model

if __name__ == "__main__":
    model = CropDiseaseClassifier(num_classes=5)
    dummy_input = torch.randn(1, 3, 224, 224)
    logits = model(dummy_input)
    energy = calculate_ood_score(logits)
    print("Logits:", logits)
    print("OOD Energy Score:", energy)
