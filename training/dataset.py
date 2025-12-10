import torch
from torch.utils.data import Dataset
import numpy as np
class SoccerDataset(Dataset):
    def __init__(self, npz_file):
        data = np.load(npz_file)
        self.obs = torch.FloatTensor(data['obs'])
        self.actions = torch.FloatTensor(data['actions']) 
        self.rewards = torch.FloatTensor(data['rewards'])
        self.kick_mask = (self.actions[:, 2] > 0).float().unsqueeze(1)
    def __len__(self): return len(self.obs)
    def __getitem__(self, idx): return {'obs': self.obs[idx], 'action': self.actions[idx], 'reward': self.rewards[idx], 'kick_mask': self.kick_mask[idx]}