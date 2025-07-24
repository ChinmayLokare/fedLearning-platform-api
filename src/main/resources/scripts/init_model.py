import argparse
import flwr as fl
import torch
import numpy as np
import torch.nn.functional as F
from torch import nn
from torch.utils.data import DataLoader, Subset
from torchvision.datasets import CIFAR10
import torchvision.transforms as transforms

class Net(nn.Module):
    def __init__(self) -> None:
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

def train(net, trainloader, epochs: int, device: str):
    """Train the network on the training set."""
    print(f"Starting training on device: {device}...")
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(net.parameters())
    net.train()
    for epoch in range(epochs):
        epoch_loss = 0.0
        for batch in trainloader:
            images, labels = batch[0].to(device), batch[1].to(device)
            optimizer.zero_grad()
            outputs = net(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        print(f"Epoch {epoch+1}: train loss {epoch_loss / len(trainloader)}")


def main():
    parser = argparse.ArgumentParser(description="Initialize a model file.")
    parser.add_argument("--model", type=str, required=True, help="Model type (e.g., CNN)")
    parser.add_argument("--out", type=str, required=True, help="Output path for the .flwr file")
    parser.add_argument("--pretrain-epochs", type=int, default=0, help="Number of epochs to pre-train on the server. Default is 0 (no pre-training).")
    args = parser.parse_args()

    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    net = Net().to(DEVICE)

    if args.pretrain_epochs > 0:
        print(f"--- Starting server-side pre-training for {args.pretrain_epochs} epochs... ---")

        # 1. Load a safe, public dataset on the server
        # We can use a small subset of the CIFAR-10 training set for this.
        pytorch_transforms = transforms.Compose(
            [transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
        )
        full_trainset = CIFAR10(root="./data", train=True, download=True, transform=pytorch_transforms)

        # Use only the first 1000 samples for pre-training to make it fast
        pretrain_subset = Subset(full_trainset, range(1000))
        pretrain_loader = DataLoader(pretrain_subset, batch_size=32, shuffle=True)

        # 2. Train the model
        train(net, pretrain_loader, epochs=args.pretrain_epochs, device=DEVICE) # Use your existing train function

        print("--- Pre-training complete. ---")
    else:
        print("--- No pre-training requested. Initializing with random weights. ---")

    # Get initial parameters
    params = [val.cpu().numpy() for _, val in net.state_dict().items()]

    # Save parameters to a file
    np.savez(args.out, *params)
    print(f"Initial model weights saved to {args.out}")

if __name__ == "__main__":
    main()