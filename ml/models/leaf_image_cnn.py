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

if __name__ == "__main__":
    model = CropDiseaseClassifier(num_classes=5)
    dummy_input = torch.randn(1, 3, 224, 224)
    logits = model(dummy_input)
    energy = calculate_ood_score(logits)
    print("Logits:", logits)
    print("OOD Energy Score:", energy)
