import threading
import pygame

pygame.mixer.init()

playlist = ["1.wav", "2.wav", "3.wav"]
current_song_index = 0

def play_pause_music(file_path):
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    global paused
    paused = False

    while True:
        if paused:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()

def control_music(a):
    global paused,current_song_index
    if a == 'p':
        paused = True
    elif a == 'u':
        paused = False
    elif a == 'q':
        pygame.mixer.music.stop()
        pygame.quit()

    elif a == 'n':
        current_song_index = (current_song_index + 1) % len(playlist)
        pygame.mixer.music.load(playlist[current_song_index])
        pygame.mixer.music.play()
    elif a == 'b':
        current_song_index = (current_song_index - 1) % len(playlist)
        pygame.mixer.music.load(playlist[current_song_index])
        pygame.mixer.music.play()
    elif a == 'e':
        pygame.mixer.music.stop()
        pygame.quit()
        exit()

def create_threading():
    threading.Thread(target=play_pause_music, args=(playlist[current_song_index],)).start()

def conctrl_music(a):
    threading.Thread(target=control_music, args=(a,)).start()

# Main program loop
while True:
    set = input("Enter your command: ")
    if set == "play":
        create_threading()
    elif set == "pause":
        conctrl_music("p")
    elif set == "resume":
        conctrl_music("u")
    elif set == "stop":
        conctrl_music("q")
        break
    elif set == "next":
        conctrl_music("n")
    elif set == "previous":
        conctrl_music("b")