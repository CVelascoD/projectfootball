# agent/actions.py

def dash(power):
    return f"(dash {power})"

def turn(angle):
    return f"(turn {angle})"

def kick(power, direction):
    return f"(kick {power} {direction})"

def move(x, y):
    return f"(move {x} {y})"

def say(msg):
    return f"(say {msg})"
