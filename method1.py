#Method 1
#main run function
def run():
    import tkinter as tk

    root = tk.Tk()

    # Get screen width and height
    screen_width = 1000
    screen_height = 600

    # Set window size to screen size
    root.geometry(f"{screen_width}x{screen_height}+100+50")
    root.state('zoomed')
    root.mainloop()
if __name__ == '__main__':
    run()
