import json

state_path = "./Weapon_server/state.json"

state = None

def get_state():
    global state
    if state == None:
        with open(state_path,"r") as f:
            state = json.load(f)
    return state
    

def disarm_state():
    global state
    state["fire_activated"] = False
    with open(state_path,"w") as f:
        json.dump(state,f)


def activate_state():
    global state
    state["fire_activated"] = True
    with open(state_path,"w") as f:
        json.dump(state,f)


def set_state_position(x,y):
    global state
    state["position_x"] = x
    state["position_y"] = y
    with open(state_path,"w") as f:
        json.dump(state,f)