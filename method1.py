# Method 1
import tkinter as tk
from PIL import Image, ImageTk
def resize_image(event):
    # Get the new size of the frame + adjustment
    new_width = event.height
    new_height = event.height
    try:
        resample = Image.Resampling.LANCZOS
    except AttributeError:
        resample = Image.ANTIALIAS

    # Resize the original image to the new size
    resized_bau = bau_logo.resize((new_width+10, new_height-10),resample)
    resized_ict = ict_min_logo.resize((new_width*2-10, new_height-10),resample)
    # Convert to Tkinter PhotoImage
    new_photo_bau = ImageTk.PhotoImage(resized_bau)
    new_photo_ict = ImageTk.PhotoImage(resized_ict)

    # Update the label with the resized image
    bau_logo_label.config(image=new_photo_bau)
    bau_logo_label.image = new_photo_bau
    ict_min_logo_label.config(image=new_photo_ict)
    ict_min_logo_label.image = new_photo_ict
# main run function
def run():
    # Color palate declaration
    col_g = '#06923E'
    col_w = '#FFFFEC'
    # Declaring main window
    app = tk.Tk()

    # Image load
    global logo,bau_logo,ict_min_logo
    logo = tk.PhotoImage(file='images//demo_logo.png')
    bau_logo =  Image.open('images//bau_logo.png')
    ict_min_logo = Image.open('images//ict_min_logo.png')
   
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
    bau_logo_tk = ImageTk.PhotoImage(bau_logo)
    global bau_logo_label
    bau_logo_label=tk.Label(head,image=bau_logo_tk,bg=col_w)
    bau_logo_label.place(relx=0.05,rely=0.05,relheight=0.9)
    
    ict_min_logo_tk = ImageTk.PhotoImage(ict_min_logo)
    global ict_min_logo_label
    ict_min_logo_label=tk.Label(head,image=ict_min_logo_tk,bg=col_w)
    ict_min_logo_label.place(relx=0.85,rely=0.05,relheight=0.9)
    head.bind('<Configure>', resize_image)

    app.mainloop()


if __name__ == '__main__':
    run()
