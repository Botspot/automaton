#!/usr/bin/python3

#This was 100% vibe-coded by Gemini 3 in about 10 minutes. Impressive.

import socket
import sys
import os
import struct
import threading
import argparse
import time
import errno

# --- Constants & Key Mappings ---
KEY_MAP = {
    'enter': 0xFF0D, 'return': 0xFF0D,
    'backspace': 0xFF08, 'tab': 0xFF09,
    'esc': 0xFF1B, 'escape': 0xFF1B,
    'delete': 0xFFFF, 'del': 0xFFFF,
    'home': 0xFF50, 'end': 0xFF57,
    'pgup': 0xFF55, 'pageup': 0xFF55,
    'pgdn': 0xFF56, 'pagedown': 0xFF56,
    'left': 0xFF51, 'up': 0xFF52,
    'right': 0xFF53, 'down': 0xFF54,
    'f1': 0xFFBE, 'f2': 0xFFBF, 'f3': 0xFFC0, 'f4': 0xFFC1,
    'f5': 0xFFC2, 'f6': 0xFFC3, 'f7': 0xFFC4, 'f8': 0xFFC5,
    'f9': 0xFFC6, 'f10': 0xFFC7, 'f11': 0xFFC8, 'f12': 0xFFC9,
    'shift': 0xFFE1, 'rshift': 0xFFE2,
    'ctrl': 0xFFE3, 'rctrl': 0xFFE4, 'control': 0xFFE3,
    'alt': 0xFFE9, 'ralt': 0xFFEA,
    'meta': 0xFFE7, 'super': 0xFFEB, 'win': 0xFFEB, 'cmd': 0xFFEB,
    'space': 0x0020
}

# State Variables
mouse_x = 0
mouse_y = 0
mouse_buttons = 0  # Bitmask: 1=Left, 2=Middle, 4=Right
vnc_sync_event = threading.Event()

def log(msg):
    print(f"[VNC-Injector] {msg}", flush=True)

# --- RFB Protocol Helpers ---

def send_key_event(sock, keysym, down=True):
    """
    RFB Msg Type 4: KeyEvent
    [1 byte type][1 byte down_flag][2 bytes pad][4 bytes keysym]
    """
    payload = struct.pack("!BBxxI", 4, 1 if down else 0, keysym)
    sock.sendall(payload)

def send_pointer_event(sock, x, y, button_mask):
    """
    RFB Msg Type 5: PointerEvent
    [1 byte type][1 byte button_mask][2 bytes x][2 bytes y]
    """
    payload = struct.pack("!BBHH", 5, button_mask, int(x), int(y))
    sock.sendall(payload)

def get_keysym(key_str):
    """Resolve a string to an X11 Keysym."""
    key_str = key_str.lower()
    if key_str in KEY_MAP:
        return KEY_MAP[key_str]
    if len(key_str) == 1:
        return ord(key_str)
    return 0

def force_vnc_sync(sock):
    """Forces VNC to sync by requesting a 1x1 pixel update and waiting for the reply."""
    global vnc_sync_event
    vnc_sync_event.clear()
    # Type 3: FramebufferUpdateRequest (1 byte type, 1 byte incremental(0), 2 bytes x, 2 bytes y, 2 bytes w, 2 bytes h)
    sync_req = struct.pack("!B B H H H H", 3, 0, 0, 0, 1, 1)
    sock.sendall(sync_req)
    # Wait up to 1 second for the server to reply and the drainer thread to flag it
    vnc_sync_event.wait(timeout=1.0)

def send_ack(pipe_path):
    """Sends ACK using non-blocking I/O, retrying if Bash isn't ready to read yet."""
    start_time = time.time()
    while time.time() - start_time < 1.0:
        try:
            # Open strictly for writing, and fail instantly if no reader exists
            fd = os.open(pipe_path, os.O_WRONLY | os.O_NONBLOCK)
            os.write(fd, b"OK\n")
            os.close(fd)
            return
        except OSError as e:
            # ENXIO (No such device or address) means Bash hasn't executed `read` yet.
            if e.errno == errno.ENXIO:
                time.sleep(0.01) # Wait a tiny fraction of a second and try again
            else:
                raise e
    log("Warning: Bash did not read the ACK in time. Continuing to prevent freeze.")

# --- Background Listeners ---

def socket_drainer(sock):
    """
    Reads data from socket to keep buffer clear and detect server disconnects.
    """
    global vnc_sync_event
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                log("Server closed connection.")
                os._exit(1)
            # Flag that the server sent data back (our sync response)
            vnc_sync_event.set()
    except Exception as e:
        pass # Socket closed locally

def pipe_monitor(pipe_path):
    """
    Monitors the named pipe and exits immediately if it is deleted.
    """
    while True:
        if not os.path.exists(pipe_path):
            log(f"Pipe {pipe_path} deleted. Exiting.")
            os._exit(0)
        time.sleep(0.5)

# --- Main Logic ---

def main():
    global mouse_x, mouse_y, mouse_buttons, vnc_sync_event

    parser = argparse.ArgumentParser(description="VNC Input Injector")
    parser.add_argument("socket", help="Path to the VNC server Unix socket")
    parser.add_argument("pipe_path", help="Path to the named pipe for input")
    args = parser.parse_args()

    sock_path = args.socket
    pipe_path = args.pipe_path

    if not os.path.exists(sock_path):
        log(f"Error: Socket file not found at {sock_path}")
        sys.exit(1)

    s = socket.socket(socket.AF_UNIX)
    
    try:
        s.connect(sock_path)
        log("Socket connected.")

        # ==============================
        #      RFB Handshake
        # ==============================
        
        # 1. Version
        server_ver = s.recv(12)
        s.send(b"RFB 003.008\n") 

        # 2. Security
        sec_data = s.recv(1024)
        if sec_data and sec_data[0] > 0:
            s.send(b"\x01") # None
        
        # 3. Auth Result
        auth_result = s.recv(4)
        if auth_result != b"\x00\x00\x00\x00":
            log("Auth failed.")
            sys.exit(1)

        # 4. Client Init
        s.send(b"\x01") # Shared

        # 5. Server Init (Drain large chunk)
        _ = s.recv(4096)

        # 6. SetPixelFormat (Required to finalize state)
        pixel_fmt = struct.pack("!B3xBBBBHHHBBB3x", 
            0, 32, 24, 0, 1, 255, 255, 255, 0, 8, 16
        )
        s.send(pixel_fmt)

        # 7. SetEncodings (Raw + DesktopSize)
        encodings = struct.pack("!B x H i i", 2, 2, 0, -223) 
        s.send(encodings)

        # 8. FramebufferUpdateRequest (Full screen to activate)
        fb_req = struct.pack("!B B H H H H", 3, 0, 0, 0, 9999, 9999)
        s.send(fb_req)
        
        # Create named pipe
        try:
            os.mkfifo(pipe_path)
            log(f"Created named pipe at {pipe_path}")
        except FileExistsError:
            log(f"Named pipe already exists at {pipe_path}")

        log("Handshake complete. Listening on named pipe...")

        # Start background thread to keep socket alive
        t = threading.Thread(target=socket_drainer, args=(s,), daemon=True)
        t.start()

        # Start background thread to monitor pipe deletion
        t2 = threading.Thread(target=pipe_monitor, args=(pipe_path,), daemon=True)
        t2.start()

        # ==============================
        #      Command Loop
        # ==============================
        
        # Loop to keep reading if multiple writers connect/disconnect
        while os.path.exists(pipe_path):
            try:
                # 1. Wait for Bash to send command
                with open(pipe_path, 'r') as pipe_in:
                    line = pipe_in.readline()

                if not line:
                    time.sleep(0.01)
                    continue

                parts = line.strip().split()
                if not parts:
                    continue

                cmd = parts[0].lower()
                valid_cmd_executed = False

                if cmd == "mousemove":
                    if len(parts) >= 3:
                        mouse_x = int(parts[1])
                        mouse_y = int(parts[2])
                        send_pointer_event(s, mouse_x, mouse_y, mouse_buttons)
                        valid_cmd_executed = True

                elif cmd == "mouseclick":
                    if len(parts) >= 2:
                        btn_id = int(parts[1])
                        mask = 0
                        if btn_id == 1: mask = 1
                        elif btn_id == 2: mask = 2
                        elif btn_id == 3: mask = 4
                        elif btn_id == 4: mask = 8 
                        elif btn_id == 5: mask = 16 

                        send_pointer_event(s, mouse_x, mouse_y, mask)
                        time.sleep(0.01)
                        send_pointer_event(s, mouse_x, mouse_y, 0)
                        valid_cmd_executed = True

                elif cmd == "keyboardtype":
                    if len(parts) >= 2:
                        text = " ".join(parts[1:])
                        for char in text:
                            k = ord(char)
                            send_key_event(s, k, True)
                            send_key_event(s, k, False)
                        valid_cmd_executed = True

                elif cmd == "keyboardshortcut":
                    if len(parts) >= 2:
                        keys = parts[1:]
                        resolved_keys = []
                        for k in keys:
                            ksym = get_keysym(k)
                            if ksym:
                                resolved_keys.append(ksym)
                                send_key_event(s, ksym, True)
                        for ksym in reversed(resolved_keys):
                            send_key_event(s, ksym, False)
                        valid_cmd_executed = True

                else:
                    log(f"Unknown command: {cmd}")

                # 2. Sync and Acknowledge
                if valid_cmd_executed:
                    force_vnc_sync(s)
                    send_ack(pipe_path)

            except OSError:
                if not os.path.exists(pipe_path):
                    sys.exit(0)
                time.sleep(0.1)

    except KeyboardInterrupt:
        pass
    finally:
        log("Closing connection.")
        s.close()

if __name__ == "__main__":
    main()
