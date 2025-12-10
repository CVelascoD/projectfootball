import torch
import torch.optim as optim
from torch.utils.data import DataLoader
import argparse
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from training.models import Actor
from training.dataset import SoccerDataset

def train(dataset_path, epochs=10, batch_size=64, lr=1e-3):
    print(f"Cargando dataset desde {dataset_path}...")
    dataset = SoccerDataset(dataset_path)
    
    # Detectar tamaño de entrada automáticamente
    sample_obs = dataset[0]['obs']
    real_obs_size = sample_obs.shape[0]
    print(f"Detectado obs_size = {real_obs_size}")

    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Entrenando en: {device}")
    
    model = Actor(obs_size=real_obs_size).to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    mse_loss = torch.nn.MSELoss()
    bce_loss = torch.nn.BCELoss()
    
    model.train()
    
    for epoch in range(epochs):
        total_loss = 0
        
        for batch in loader:
            obs = batch['obs'].to(device)
            target_act = batch['action'].to(device)
            target_kick_prob = batch['kick_mask'].to(device)
            
            optimizer.zero_grad()
            
            p_dash, p_turn, p_kick_prob, p_kick_pow, p_kick_ang = model(obs)
            
            # 1. Movimiento
            t_dash = target_act[:, 0].unsqueeze(1) / 100.0
            t_turn = target_act[:, 1].unsqueeze(1) / 180.0
            loss_move = mse_loss(p_dash, t_dash) + mse_loss(p_turn, t_turn)
            
            # 2. Kick Decision
            loss_kick_dec = bce_loss(p_kick_prob, target_kick_prob)
            
            # 3. Kick Params
            mask = target_kick_prob.bool()
            loss_kick_p = 0
            if mask.any():
                t_k_pow = target_act[mask.squeeze(), 2] / 100.0
                t_k_ang = target_act[mask.squeeze(), 3] / 180.0
                
                loss_kick_p = mse_loss(p_kick_pow[mask].squeeze(), t_k_pow) + \
                              mse_loss(p_kick_ang[mask].squeeze(), t_k_ang)
            
            loss = loss_move + loss_kick_dec + loss_kick_p
            
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            
        print(f"Epoch {epoch+1}/{epochs} - Loss: {total_loss/len(loader):.4f}")
        
    os.makedirs("models", exist_ok=True)
    torch.save(model.state_dict(), "models/actor_v1.pth")
    print("Modelo guardado en models/actor_v1.pth")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="training_data.npz")
    args = parser.parse_args()
    train(args.data)