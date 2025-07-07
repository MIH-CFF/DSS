# Method 1

import tkinter as tk
from PIL import Image, ImageTk
def resize_image(event):
    # Get the new size of the frame
    new_width = event.width
    new_height = event.height

    # Resize the original image to the new size
    resized = original_image.resize((new_width, new_height), Image.ANTIALIAS)

    # Convert to Tkinter PhotoImage
    new_photo = ImageTk.PhotoImage(resized)

    # Update the label with the resized image
    label.config(image=new_photo)
    label.image = new_photo
# main run function
def run():
    # Color palate declaration
    col_g = '#06923E'
    col_w = '#FFFFEC'
    # Declaring main window
    app = tk.Tk()

    # Image load
    logo = tk.PhotoImage(file='images//demo_logo.png')
    bau_logo = tk.PhotoImage(file='images//bau_logo.png')
    ict_min_logo = tk.PhotoImage(file='images//ict_min_logo.png')

    # Set icon & title
    app.iconphoto(False, logo)
    app.title("DNA SEQUENCE SIMILARITY ANALYZER")

    # Get screen width and height
    screen_width = 1000
    screen_height = 600

    # Setting a regular window size to screen size
    app.geometry(f"{screen_width}x{screen_height}+100+50")

    # Setting default window size to screen size
    app.state('zoomed')

    # Declaring header
    head=tk.Frame(app,bg=col_w)
    head.place(relx=0,rely=0,relheight=0.1,relwidth=1)

    # Head contents
    bau_logo_label=tk.Label(head,image=bau_logo)
    bau_logo_label.place(relx=0.1,rely=0.1,relheight=0.8)

    app.mainloop()


if __name__ == '__main__':
    run()
