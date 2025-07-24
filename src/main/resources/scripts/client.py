import argparse
import flwr as fl
from collections import OrderedDict
from typing import List

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
from flwr_datasets import FederatedDataset

# --- Configuration ---
NUM_PARTITIONS = 10  # Total number of partitions available in the dataset
BATCH_SIZE = 32
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Client operating on {DEVICE}")


# --- Data Loading Logic ---
def load_datasets(partition_id: int):
    """Loads the training and validation data for a given client partition."""
    fds = FederatedDataset(dataset="cifar10", partitioners={"train": NUM_PARTITIONS})
    partition = fds.load_partition(partition_id)
    partition_train_test = partition.train_test_split(test_size=0.2, seed=42)
    pytorch_transforms = transforms.Compose(
        [transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
    )

    def apply_transforms(batch):
        batch["img"] = [pytorch_transforms(img) for img in batch["img"]]
        return batch

    partition_train_test = partition_train_test.with_transform(apply_transforms)
    trainloader = DataLoader(partition_train_test["train"], batch_size=BATCH_SIZE, shuffle=True)
    valloader = DataLoader(partition_train_test["test"], batch_size=BATCH_SIZE)
    # The global testloader isn't strictly needed by the client, but we can return it.
    testset = fds.load_split("test").with_transform(apply_transforms)
    testloader = DataLoader(testset, batch_size=BATCH_SIZE)
    return trainloader, valloader, testloader


# --- Model Definition ---
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


# --- Training and Utility Functions ---
def train(net, trainloader, epochs: int):
    """Train the network on the training set."""
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(net.parameters())
    net.train()
    for epoch in range(epochs):
        for batch in trainloader:
            images, labels = batch["img"].to(DEVICE), batch["label"].to(DEVICE)
            optimizer.zero_grad()
            outputs = net(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

def test(net, testloader):
    """Evaluate the network on the test set."""
    criterion = torch.nn.CrossEntropyLoss()
    correct, total, loss = 0, 0, 0.0
    net.eval()
    with torch.no_grad():
        for batch in testloader:
            images, labels = batch["img"].to(DEVICE), batch["label"].to(DEVICE)
            outputs = net(images)
            loss += criterion(outputs, labels).item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    loss /= len(testloader.dataset)
    accuracy = correct / total
    return loss, accuracy

def set_parameters(net, parameters: List[np.ndarray]):
    params_dict = zip(net.state_dict().keys(), parameters)
    state_dict = OrderedDict({k: torch.Tensor(v) for k, v in params_dict})
    net.load_state_dict(state_dict, strict=True)

def get_parameters(net) -> List[np.ndarray]:
    return [val.cpu().numpy() for _, val in net.state_dict().items()]


# --- Flower Client Definition ---
class FlowerClient(fl.client.NumPyClient):
    def __init__(self, partition_id,  net, trainloader, valloader):
        self.partition_id = partition_id
        self.net = net
        self.trainloader = trainloader
        self.valloader = valloader

    def get_parameters(self, config):
        print(f"[Client {self.partition_id}] get_parameters")
        return get_parameters(self.net)

    def fit(self, parameters, config):
        print(f"[Client {self.partition_id}] fit, config: {config}")
        set_parameters(self.net, parameters)
        train(self.net, self.trainloader, epochs=1)
        # The fit method in NumPyClient should return 3 values.
        return get_parameters(self.net), len(self.trainloader.dataset), {}

    def evaluate(self, parameters, config):
        print(f"[Client {self.partition_id}] evaluate, config: {config}")
        set_parameters(self.net, parameters)
        loss, accuracy = test(self.net, self.valloader)
        # The evaluate method in NumPyClient should return 3 values.
        return float(loss), len(self.valloader.dataset), {"accuracy": float(accuracy)}


# --- Main execution block ---
def main():
    """Create and start a Flower client."""
    parser = argparse.ArgumentParser(description="Flower Client")
    parser.add_argument("--project-id", type=str, required=True, help="The ID of the project to join")
    parser.add_argument("--server-address", type=str, required=True, help="Address of the Flower server (e.g., localhost:51455)")

    # --- FIX 1: Add a command-line argument for the partition_id ---
    parser.add_argument(
        "--partition-id",
        type=int,
        required=True,
        choices=range(0, NUM_PARTITIONS),
        help=f"The partition ID for this client (an integer from 0 to {NUM_PARTITIONS-1})."
    )
    args = parser.parse_args()

    # Load model and move it to the correct device

    net = Net().to(DEVICE)

    # --- FIX 2: Load the specific data partition for this client ---
    print(f"Loading data for partition {args.partition_id}...")
    trainloader, valloader, _ = load_datasets(partition_id=args.partition_id)
    print("Data loaded successfully.")

    # --- FIX 3: Create the FlowerClient with all required arguments ---
    client = FlowerClient(
        partition_id=args.partition_id,
        net=net,
        trainloader=trainloader,
        valloader=valloader
    )

    # Start the client which will connect to the server
    print(f"Starting Flower client for project {args.project_id}...")
    fl.client.start_client(
        server_address=args.server_address,
        client=client
    )
    print("Client disconnected.")

if __name__ == "__main__":
    main()