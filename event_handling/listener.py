import uuid
import serial
import threading
from enum import Enum, auto
from time import sleep
from typing import Callable

class MicrobitEvent(Enum):
    BUTTON_A_DOWN          = auto()
    BUTTON_A_UP            = auto()
    BUTTON_B_DOWN          = auto()
    BUTTON_B_UP            = auto()
    ACCELEROMETER_POSITION = auto()

class _MicrobitEventMessages(Enum):
    BUTTON_A_PRESSED = 'btna'
    BUTTON_B_PRESSED = 'btnb'

    @classmethod
    def from_message(cls, message: str):
        try:
            return cls(message)
        except ValueError:
            raise ValueError(f"Cannot convert message: [{message}] to MicrobitEvent")

def _new_clean_microbit_state():
    state = {}
    for event_message in _MicrobitEventMessages:
        state[event_message]  = False
    
    return state

def _microbit_state_from_event_messages(events: list[_MicrobitEventMessages]):
    state = _new_clean_microbit_state()
    for event in events:
        state[event] = True

    return state


class MicrobitListener:
    def __init__(self, device: str="/dev/ttyACM0"):
        self.current_events = {}
        for event in MicrobitEvent:
            self.current_events[event] = {}

        self.serial_reader = serial.Serial(device, 115200, timeout=0.1)

    def on(self, event: MicrobitEvent, callback: Callable[[], None]) -> uuid.UUID:
        call_uuid = uuid.uuid4()
        self.current_events[event][call_uuid] = callback
        return call_uuid

    def remove_call(self, event: MicrobitEvent, uuid: uuid.UUID):
        if uuid in self.current_events[event].keys():
            del self.current_events[event][uuid]

    def start_listening(self):
        self._stop_event = threading.Event()
        self._listener_thread = threading.Thread(target=self._event_handler)
        self._listener_thread.start()

    def stop_listening(self):
        if hasattr(self, '_stop_event') and hasattr(self, '_listener_thread'): 
            self._stop_event.set()
            self._listener_thread.join()

    def _event_handler(self):
        last_state = _new_clean_microbit_state()

        while not self._stop_event.is_set():
            message = self.serial_reader.readline().decode().strip()

            event_messages = message.split(',') if message else []

            microbit_event_messages = [_MicrobitEventMessages.from_message(message) for message in event_messages]
            new_state = _microbit_state_from_event_messages(microbit_event_messages)
            microbit_events = []

            # BUTTON A EVENTS
            if new_state[_MicrobitEventMessages.BUTTON_A_PRESSED] and not last_state[_MicrobitEventMessages.BUTTON_A_PRESSED]:
                microbit_events.append(MicrobitEvent.BUTTON_A_DOWN)
            if not new_state[_MicrobitEventMessages.BUTTON_A_PRESSED] and last_state[_MicrobitEventMessages.BUTTON_A_PRESSED]:
                microbit_events.append(MicrobitEvent.BUTTON_A_UP)

            # BUTTON B EVENTS
            if new_state[_MicrobitEventMessages.BUTTON_B_PRESSED] and not last_state[_MicrobitEventMessages.BUTTON_B_PRESSED]:
                microbit_events.append(MicrobitEvent.BUTTON_B_DOWN)
            if not new_state[_MicrobitEventMessages.BUTTON_B_PRESSED] and last_state[_MicrobitEventMessages.BUTTON_B_PRESSED]:
                microbit_events.append(MicrobitEvent.BUTTON_B_UP)
            
            last_state = new_state

            for event in microbit_events:
                for callback in self.current_events[event].values():
                    callback()


if __name__ == "__main__":
    def button_a_down():
        print("Button A is down")

    def button_a_up():
        print("Button A is up")

    def button_b_down():
        print("Button B is down")

    def button_b_up():
        print("Button B is up")

    listener = MicrobitListener()
    listener.on(MicrobitEvent.BUTTON_A_DOWN, button_a_down)
    listener.on(MicrobitEvent.BUTTON_A_UP, button_a_up)

    listener.on(MicrobitEvent.BUTTON_B_DOWN, button_b_down)
    listener.on(MicrobitEvent.BUTTON_B_UP, button_b_up)

    listener.start_listening()

    sleep(15)

    listener.stop_listening()