import torch
import torch.nn as nn
import torch.nn.functional as F
class Actor(nn.Module):
    def __init__(self, obs_size=54):
        super().__init__()
        self.fc1 = nn.Linear(obs_size, 128)
        self.fc2 = nn.Linear(128, 128)
        self.head_dash = nn.Linear(128, 1)
        self.head_turn = nn.Linear(128, 1)
        self.head_kick_prob = nn.Linear(128, 1)
        self.head_kick_pow = nn.Linear(128, 1)
        self.head_kick_ang = nn.Linear(128, 1)
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return torch.sigmoid(self.head_dash(x)), torch.tanh(self.head_turn(x)), torch.sigmoid(self.head_kick_prob(x)), torch.sigmoid(self.head_kick_pow(x)), torch.tanh(self.head_kick_ang(x))
class Critic(nn.Module):
    def __init__(self, obs_size=54):
        super().__init__()
        self.fc1, self.fc2, self.value_head = nn.Linear(obs_size, 128), nn.Linear(128, 128), nn.Linear(128, 1)
    def forward(self, x): return self.value_head(F.relu(self.fc2(F.relu(self.fc1(x)))))