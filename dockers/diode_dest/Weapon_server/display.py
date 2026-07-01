from textual.app import App, ComposeResult
from textual.widgets import Digits,Static
from textual.color import Color
from datetime import timedelta,datetime,timezone
from state import get_state

FREQUENCY  = 1/10

class Position(Static):
    
    def on_mount(self) -> None:
        global FREQUENCY
        self.update_text = self.set_interval(FREQUENCY,self.update_text)

    def update_text(self) -> None:
        current_state = get_state()
        if current_state["fire_activated"]:
            txt= "fire coordonates %f - %f" % (current_state["position_x"],current_state["position_y"]) 
        else:
            txt= ""  
        self.update(txt)

class Fire(Static):
    
    def on_mount(self) -> None:
        global FREQUENCY
        self.update_text = self.set_interval(FREQUENCY,self.update_text)

    def update_text(self) -> None:
        current_state = get_state()
        txt = ""
        if current_state["fire_activated"]:
            txt= "Fire mode activated"   
        else:
            txt= current_state["flag"]   
        self.update(txt)


class Countdown(Digits):
    start_time = 0
    countdown = 0
    
    def on_mount(self) -> None:
        global FREQUENCY
        current_state = get_state()
        self.start_time = datetime.fromisoformat(current_state["fire_date"])
        self.update_timer = self.set_interval(FREQUENCY,self.update_time)
        self.styles.background = Color.parse("green")    

    def update_time(self) -> None:
        current_state = get_state()
        
        if current_state["fire_activated"]:
            self.styles.background = Color.parse("red")
            self.countdown =  self.start_time- datetime.now(timezone.utc)
            self.update(str(self.countdown))
        else:
            self.styles.background = Color.parse("green")    


class WeaponApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    #Countdown {
        border: double green;
        width: auto;
    }
    #Fire {
        border: double green;
        width: auto;
    }
    """

    def compose(self) -> ComposeResult:
        self.theme ="tokyo-night" 
        yield Fire()
        yield Position()
        yield Countdown()


def display_routine():
    static_ap = WeaponApp()
    static_ap.run()