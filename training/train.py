import torch
import torch.optim as optim
from torch.utils.data import DataLoader
import argparse
import os
from training.models import Actor
from training.dataset import SoccerDataset

def train(dataset_path, epochs=10, batch_size=64, lr=1e-3):
    dataset = SoccerDataset(dataset_path)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = Actor().to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    mse, bce = torch.nn.MSELoss(), torch.nn.BCELoss()
    model.train()
    
    for epoch in range(epochs):
        total_loss = 0
        for batch in loader:
            obs, target_act, target_kick_prob = batch['obs'].to(device), batch['action'].to(device), batch['kick_mask'].to(device)
            optimizer.zero_grad()
            p_dash, p_turn, p_kick_prob, p_kick_pow, p_kick_ang = model(obs)
            
            loss_move = mse(p_dash, target_act[:, 0].unsqueeze(1)/100.0) + mse(p_turn, target_act[:, 1].unsqueeze(1)/180.0)
            loss_kick_dec = bce(p_kick_prob, target_kick_prob)
            loss_kick_p = 0
            if (mask := target_kick_prob.bool()).any():
                loss_kick_p = mse(p_kick_pow[mask], target_act[mask.squeeze(), 2].unsqueeze(1)/100.0) + mse(p_kick_ang[mask], target_act[mask.squeeze(), 3].unsqueeze(1)/180.0)
            
            loss = loss_move + loss_kick_dec + loss_kick_p
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch+1} - Loss: {total_loss/len(loader):.4f}")
    os.makedirs("models", exist_ok=True)
    torch.save(model.state_dict(), "models/actor_v1.pth")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="training_data.npz")
    args = parser.parse_args()
    train(args.data)