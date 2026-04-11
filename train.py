import torch
import torch.nn as nn
import torch.optim as optim
import json
from torch.cuda.amp import GradScaler

class ConvNet(nn.Module):
    def __init__(self, output_size=10, dropout_prob=0.2):
        super(ConvNet, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2, padding=0)
        self.fc1 = nn.Linear(4096, 2048)
        self.fc2 = nn.Linear(2048, 1024)
        self.fc3 = nn.Linear(1024, 512)
        self.fc4 = nn.Linear(512, output_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout_prob)

    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = x.view(-1, 4096)
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.relu(self.fc3(x))
        x = self.dropout(x)
        x = self.fc4(x)
        return x

class Trainer():
    def __init__(self, output_size=4, patience=2, batch_size=64, device='cuda:0' if torch.cuda.is_available() else 'cpu', lambda_l2=1e-6, lambda_l1=1e-6, dropout_prob=0.2, lr=0.001):
        self.model = ConvNet(output_size=output_size, dropout_prob=dropout_prob).to(device)
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr, weight_decay=lambda_l2)
        self.patience = patience
        self.batch_size = batch_size
        self.device = device
        self.l1_lambda = lambda_l1
        self.best_val_loss = float('inf')
        torch.compile(self.model)

    def train(self, train_loader, val_loader, trial=None, early_stopping=True):
        epoch = 0
        epochs_without_improvement = 0
        best_val_value = float('inf')
        self.val_loader = val_loader
        self.train_loader = train_loader
        self.loss_dict = {"trainLoss":[], "valLoss":[], "valAcc":[]}
        batch = (0, len(self.train_loader))

        while True:
            self.model.train()
            train_loss = 0.0
            for i, (inputs, labels) in enumerate(self.train_loader):
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                self.optimizer.zero_grad()
                outputs = self.model(inputs)
                loss = self.criterion(outputs, labels)
                loss += self.l1_lambda * torch.norm(self.model.conv1.weight, 1)
                loss.backward()
                self.optimizer.step()
                train_loss += loss.item()
                batch = (i+1, len(self.train_loader))

            train_loss /= len(self.train_loader)

            val_loss = 0.0
            accuracy = 0.0
            self.model.eval()
            with torch.no_grad():
                for i, (inputs, labels) in enumerate(self.val_loader):
                    inputs, labels = inputs.to(self.device), labels.to(self.device)
                    outputs = self.model(inputs)
                    loss = self.criterion(outputs, labels)
                    val_loss += loss.item()
                    accuracy += (outputs.argmax(dim=1) == labels).sum().item()

            val_loss /= len(self.val_loader)
            accuracy /= len(self.val_loader.dataset)

            self.loss_dict["trainLoss"].append(train_loss)
            self.loss_dict["valLoss"].append(val_loss)
            self.loss_dict["valAcc"].append(accuracy)

            with open('./log/loss.json', 'w') as f:
                json.dump(self.loss_dict, f)

            if trial:
                trial.report(val_loss, epoch)
                if trial.should_prune():
                    with open('./log/log.log', 'a') as f:
                        f.write('Early stopping at epoch: {}\n'.format(epoch + 1))
                    return self.model

            if early_stopping:
                if val_loss < best_val_value:
                    best_val_value = val_loss
                    self.best_val_loss = val_loss
                    epochs_without_improvement = 0
                    self.save_model("./models/model.pth")
                else:
                    epochs_without_improvement += 1

                if epochs_without_improvement == self.patience:
                    return self.model

            epoch += 1

    def save_model(self, path):
        torch.save(self.model.state_dict(), path)

    def load_model(self, path):
        self.model.load_state_dict(torch.load(path))

    def use_model(self, inputs):
        self.model.eval()
        with torch.no_grad():
            inputs = inputs.tensors[0].to(self.device).view(-1, 1, 32, 32)
            outputs = self.model(inputs)
        return outputs
