import platform
from actions import get_target,set_target,fire,disarm


def server_routine():
    if platform.system() == "Windows":
        from Weapon_common.pipe_win import create_and_connect,pipe_read,pipe_send
    else:
        from Weapon_common.pipe_linux import create_and_connect,pipe_read,pipe_send

    from Weapon_common.serialize import Message,OperationCode

    # create pipe +  connect (Wait authent connection)
    (read_pipe,write_pipe) = create_and_connect()


    while True:
        request_data = pipe_read(read_pipe)
        #print("Read data from pipe: {}".format(request_data))
        if request_data == None:
            print("Reconnection attempt")
            (read_pipe,write_pipe) = create_and_connect()
            continue

        request = Message.unpack(request_data)


        # get Target
        if request.operation_code == OperationCode.GET_TARGET.value:
            #print("get target request")
            response = get_target(request)

        # set Target
        elif request.operation_code == OperationCode.SET_TARGET.value:

            response = set_target(request)

        # fire
        elif request.operation_code == OperationCode.FIRE.value:
            #print("FIRE!")        
            response = fire(request)

        # disarm
        elif request.operation_code == OperationCode.DISARM.value:
            #print("DISARM!")  
            response = disarm(request)
        
        elif request.operation_code == OperationCode.IMPERSONATE.value:
            response = impersonate(request, target_user)

        else:
            print("Invalid operation code")
            

        serialized_response = response.pack()
        print(serialized_response)
        pipe_send(write_pipe,serialized_response)


if __name__ == "__main__":
    server_routine()