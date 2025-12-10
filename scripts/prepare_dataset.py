import json
import numpy as np
import argparse
import glob
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from training.features import FeatureExtractor
from training.rewards import RewardCalculator
from agent.state import WorldModel

def process_log(filepath):
    print(f"Procesando {filepath}...")
    team_side = 'r' if "Right" in os.path.basename(filepath) else 'l'
    extractor, rewarder = FeatureExtractor(), RewardCalculator(team_side)
    observations, actions, rewards, prev_wm = [], [], [], None
    
    with open(filepath, 'r') as f:
        for line in f:
            try:
                data = json.loads(line)
                wm = WorldModel()
                wm.time, wm.stamina, wm.play_mode, wm.ball = data.get("time"), data.get("stamina"), data.get("play_mode"), data.get("ball")
                
                obs = extractor.get_observation(wm)
                act = data.get("action", {})
                act_vec = [act.get("dash", 0.0), act.get("turn", 0.0), 0.0, 0.0]
                if act.get("kick"): act_vec[2], act_vec[3] = act["kick"]
                
                rew = rewarder.calculate(wm, prev_wm, act) if prev_wm else 0.0
                observations.append(obs); actions.append(act_vec); rewards.append(rew)
                prev_wm = wm
            except: continue
    return np.array(observations), np.array(actions), np.array(rewards)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--logdir", default="logs")
    parser.add_argument("--output", default="training_data.npz")
    args = parser.parse_args()
    all_obs, all_acts, all_rews = [], [], []
    for f in glob.glob(os.path.join(args.logdir, "*.jsonl")):
        o, a, r = process_log(f)
        if len(o): all_obs.append(o); all_acts.append(a); all_rews.append(r)
    if all_obs:
        np.savez_compressed(args.output, obs=np.concatenate(all_obs), actions=np.concatenate(all_acts), rewards=np.concatenate(all_rews))
        print(f"Dataset generado en {args.output}")

if __name__ == "__main__": main()