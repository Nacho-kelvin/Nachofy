import os
import sys
import ctypes
import vlc
import time
from pathlib import Path
import tkinter as tk  
from ctypes import windll  

# ======================
# VLC PATH CONFIGURATION
# ======================
VLC_INSTALL_PATH = r"C:\Program Files\VideoLAN\VLC"

def verify_vlc_installation():
    """Ensure VLC is properly installed and accessible"""
    dll_path = os.path.join(VLC_INSTALL_PATH, "libvlc.dll")
    if not os.path.exists(dll_path):
        print(f"❌ Error: VLC not found at {VLC_INSTALL_PATH}")
        print("Please install VLC from https://www.videolan.org/vlc/")
        print("Make sure to check 'Add to PATH' during installation")
        sys.exit(1)
    
    try:
        os.add_dll_directory(VLC_INSTALL_PATH)
        ctypes.CDLL(dll_path)
        print("✅ VLC initialized successfully")
    except Exception as e:
        print(f"❌ VLC initialization failed: {e}")
        sys.exit(1)

verify_vlc_installation()

class MediaPlayer:
    
    def __init__(self):
        self.set_window_icon()  # Add this line as the FIRST LINE in __init__
        self.instance = vlc.Instance("--no-xlib --quiet")
        # ... rest of your existing __init__ code ...
    
    def set_window_icon(self):
        """Sets application icon (visible in taskbar)"""
        if os.name == 'nt':  # Windows only
            try:
                # Create minimal tkinter window
                root = tk.Tk()
                root.withdraw()
                
                # Load your icon (change path to your actual .ico file)
                icon_path = r"C:\KELLY (PROJECT HUB)\NACHOFY\Icon\kelly.ico"
                if os.path.exists(icon_path):
                    root.iconbitmap(icon_path)
                    
                    # Force taskbar icon refresh
                    windll.shell32.SetCurrentProcessExplicitAppUserModelID("MzikiPlayer.1.0")
            except Exception as e:
                print(f"⚠️ Could not set icon: {e}")
    def __init__(self):
        self.instance = vlc.Instance("--no-xlib --quiet")
        self.player = self.instance.media_player_new()
        self.playlist = []
        self.current_index = 0
        self.volume = 70
        self.is_paused = False

    def build_playlist(self):
        """Load all media files from specified folders"""
        media_folders = {
            "audio": r"C:\KELLY (PROJECT HUB)\NACHOFY\Mziki",
            "video": r"C:\KELLY (PROJECT HUB)\NACHOFY\Videos"
        }
        
        extensions = {
            "audio": [".mp3", ".wav"],
            "video": [".mp4", ".avi", ".mkv"]
        }
        
        self.playlist = []
        for media_type, folder in media_folders.items():
            if not os.path.exists(folder):
                print(f"⚠️ Folder not found: {folder}")
                continue
                
            for file in os.listdir(folder):
                if any(file.lower().endswith(ext) for ext in extensions[media_type]):
                    full_path = os.path.join(folder, file)
                    self.playlist.append((media_type, full_path))
        
        if not self.playlist:
            raise Exception("No playable files found!")

    def play_current(self):
        """Play the currently selected media file"""
        if not self.playlist:
            return False
            
        media_type, media_path = self.playlist[self.current_index]
        
        try:
            self.player.stop()
            media = self.instance.media_new(media_path)
            self.player.set_media(media)
            
            if media_type == "video" and os.name == 'nt':
                hwnd = ctypes.windll.user32.GetForegroundWindow()
                self.player.set_hwnd(hwnd)
            
            if self.player.play() == -1:
                raise Exception("Playback failed")
            
            timeout = 5
            start_time = time.time()
            while not self.player.is_playing():
                if time.time() - start_time > timeout:
                    raise Exception("Playback timeout")
                time.sleep(0.1)
            
            self.player.audio_set_volume(self.volume)
            print(f"\n{'🎵' if media_type == 'audio' else '🎬'} Now Playing: {Path(media_path).name}")
            return True
            
        except Exception as e:
            print(f"❌ Error playing {Path(media_path).name}: {e}")
            return False

    def toggle_pause(self):
        if self.player.is_playing():
            self.player.pause()
            self.is_paused = True
            print("⏸ Paused")
        else:
            self.player.play()
            self.is_paused = False
            print("▶ Resumed")

    def next_track(self):
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play_current()

    def previous_track(self):
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play_current()

    def set_volume(self, change):
        self.volume = max(0, min(100, self.volume + change))
        self.player.audio_set_volume(self.volume)
        print(f"🔊 Volume: {self.volume}%")

    def run(self):
        """Main player interface"""
        try:
            self.build_playlist()
            self.play_current()
            
            print("\n🎶 Media Player Controls:")
            print("[P] Play/Pause")
            print("[N] Next Track")
            print("[B] Previous Track")
            print("[+] Volume Up")
            print("[-] Volume Down")
            print("[Q] Quit")
            
            while True:
                if not self.is_paused and not self.player.is_playing():
                    self.next_track()
                
                try:
                    cmd = input("\n> ").lower()
                    
                    if cmd == 'p': self.toggle_pause()
                    elif cmd == 'n': self.next_track()
                    elif cmd == 'b': self.previous_track()
                    elif cmd == '+': self.set_volume(10)
                    elif cmd == '-': self.set_volume(-10)
                    elif cmd == 'q': break
                    else: print("Invalid command")
                
                except (KeyboardInterrupt, EOFError):
                    break
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        finally:
            self.player.stop()
            print("🎧 Player closed")
            return True

if __name__ == "__main__":
    player = MediaPlayer()
    if not player.run():
        sys.exit(1)