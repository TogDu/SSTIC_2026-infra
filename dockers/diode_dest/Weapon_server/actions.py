from Weapon_common.serialize import Message,OperationCode
from state import get_state,activate_state,disarm_state,set_state_position

def get_target(request):

    current_state = get_state()

    response = Message(OperationCode.GET_TARGET)
    response.add_float(current_state["position_x"])
    response.add_float(current_state["position_y"])

    return response


def set_target(request):
    
    set_state_position(request.get_float(0),request.get_float(1))
    response = Message(OperationCode.SET_TARGET)

    return response

def fire(request):
    current_state = get_state()
    response = Message(OperationCode.FIRE)
    if current_state["fire_activated"]:
        response.error_code = 1
        response.add_string("System already activated")
    else:    
        current_state["fire_activated"] = True
        activate_state()
        response.add_string("Fire mode activated")

    return response

def disarm(request):

    current_state = get_state()

    response = Message(OperationCode.DISARM)
    if not current_state["fire_activated"]:
        response.error_code = 1
        response.add_string("System already disarmed")
    else:    
        current_state["fire_activated"] = False
        response.add_string(current_state["flag"])
        disarm_state()
        
    return response

