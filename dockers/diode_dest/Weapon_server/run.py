import threading
from server import server_routine
from  display import display_routine

if __name__ == "__main__":
    server_thread = threading.Thread(target=server_routine)
    server_thread.start()
    display_routine()
    server_thread.join()
    