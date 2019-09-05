from tkinter import *
from PIL import Image, ImageTk

class Region(Canvas):
    pass

    def __init__(self, master, region, name='', *args, **kwargs):
        self.master = master
        self.region = region
        self.name = name
        self.image = Image.open(region).resize((957, 1000))
        self.aspect_ratio = self.image.width / self.image.height
        self.render = ImageTk.PhotoImage(self.image)
        super().__init__(master, *args, **kwargs)
        self.show_image()

    def show_image(self):
        self.create_image(0, 0, image = self.render, anchor = NW, tag = 'map')

    #def fit_image(self, event):
    #    self.delete('map')
    #    ar = event.width / event.height
    #    if (ar < self.aspect_ratio):
    #        ratio = self.winfo_reqwidth() / self.image.width
    #    else:
    #        ratio = self.winfo_reqheight() / self.image.height
    #    new_dim = (self.image.width * ratio, self.image.height * ratio)
    #    img = self.image.resize(new_dim)
    #    rend = ImageTk.PhotoImage(img)
    #    self.create_image(0, 0, image = rend, anchor = NW, tag = 'map')


def main():
    root = Tk()
    root.title('Project:Gorgon Survey Tool')

    canvas = Region(root, 'serbule_map.png', 'Serbule', width = 957, height = 1000, bg='black')
    canvas.pack(side=LEFT)

    inventory = Frame(root, width = 500, height = 1000, bg='#423930')
    inventory.pack(side=RIGHT)
    
    root.mainloop()


if __name__ == "__main__":
    main()