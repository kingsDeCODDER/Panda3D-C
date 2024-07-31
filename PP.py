from math import pi
from panda3d.core import Filename, getModelPath, CollisionTraverser, CollisionNode, CollisionRay, CollisionHandlerQueue, BitMask32
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectEntry, DirectLabel
from direct.task import Task
import os

class HouseApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.house_dir = r'C://Panda3D-1.10.14-x64'
        
        self.houses = {}
        self.comments = {}
        self.current_house = None
        self.comment_label = None
        self.load_houses()
        self.setup_controls()
        self.taskMgr.add(self.task_loop,"task loop")
        self.comment_entry = DirectEntry(text="", scale=0.05, command=self.on_enter, initialText="", numLines=3,width=25, focus=0)
        self.comment_entry.setPos(-1.5 , 0, -0.8) 
        self.setup_collision_detection() 

    def load_houses(self):
        getModelPath().appendPath(Filename.fromOsSpecific(self.house_dir))
        if not os.path.exists(self.house_dir):
            print(f"Error: The directory {self.house_dir} does not exist!")
            return

        for file_name in os.listdir(self.house_dir):
            if file_name.endswith(".glb"):  # Assuming .glb files for Panda3D
                house_path =file_name # Must be in same directory as code.
                try:
                    house = self.loader.loadModel(house_path)
                    house.setScale(0.25)
                    house.reparentTo(self.render)
                    house.setPos(len(self.houses) * 10, 16, 0)  # Spread houses along the x-axis
                    house_name = os.path.splitext(file_name)[0]
                    house.setName(house_name)
                    self.houses[house_name] = house
                    self.comments[house_name] = []
                    base.disableMouse()
                    house.setTag('name',house_name)
                    house.setTag('id',str(len(self.houses)))
                    house.setPythonTag('onClick',self.on_house_click)
                    house.setCollideMask(BitMask32.bit(1))
                except Exception as e:
                    print(f"Error loading model {house_path}: {e}")

    def task_loop(self,task):
        self.camera.setPos(self.camera.getX(), self.camera.getY(), 2)
        return task.cont

    def setup_controls(self):
        self.accept("arrow_left", self.move_left)
        self.accept("arrow_right", self.move_right)
        self.accept("arrow_up", self.move_forward)
        self.accept("arrow_down", self.move_back)
        self.accept("a", self.rotate_left)
        self.accept("d", self.rotate_right)
        self.accept("c", self.prompt_for_comment)
        self.accept("v", self.view_comments)
        

    def move_left(self):
       self.camera.setX(self.camera.getX() - 1)

    def move_right(self):
        self.camera.setX(self.camera.getX() + 1)
    
    def move_forward(self):
        self.camera.setY(self.camera.getY()+1)
    
    def move_back(self):
        self.camera.setY(self.camera.getY() - 1)
    
    def rotate_left(self):
        self.camera.setH(self.camera.getH() +15)
    
    def rotate_right(self):
        self.camera.setH(self.camera.getH() -15)

    def on_enter(self, text):
        if self.current_house and text:
            house_Name=self.current_house.getName()
            self.comments[house_Name].append(text)
        self.comment_entry.enterText('')
        self.current_house= None
      
    def setup_collision_detection(self):# note this copied from Kingsley and ultimately chatGPT
        self.picker = CollisionTraverser()
        self.picker_handler = CollisionHandlerQueue()
        self.picker_node = CollisionNode('mouseRay')
        self.picker_np = self.camera.attachNewNode(self.picker_node)
        self.picker_node.setFromCollideMask(BitMask32.bit(1))
        self.picker_ray = CollisionRay()
        self.picker_node.addSolid(self.picker_ray)
        self.picker.addCollider(self.picker_np, self.picker_handler)
        self.accept("mouse1", self.on_click)


    def focus_comment_entry(self):
        self.comment_entry['focus'] = 1

    def prompt_for_comment(self):
        self.comment_entry['focus'] = 1  

    def view_comments(self):
        if self.current_house is not None:
            house_name = self.current_house.getName()
            if house_name in self.comments:
                for comment in self.comments[house_name]:
                    print(f"Comment for {house_name}: {comment}")
            else:
                print("No comments for this house.")
        else:
            print("House not selected")

    def on_house_click(self, house):
        self.current_house = house

    def on_click(self):# Also from Kingsley and ultmately chatGPT
        if self.mouseWatcherNode.hasMouse():
            mpos = self.mouseWatcherNode.getMouse()
            self.picker_ray.setFromLens(self.camNode, mpos.getX(), mpos.getY())
            self.picker.traverse(self.render)
            if self.picker_handler.getNumEntries() > 0:
                self.picker_handler.sortEntries()
                picked_node = self.picker_handler.getEntry(0).getIntoNodePath()
                house = picked_node.findNetTag('name')
                if house:
                    on_click_func = house.getPythonTag('onClick')
                    if on_click_func:
                       on_click_func(house)
            else:
                self.current_house=None
                self.comment_entry['focus']=0  #releases focus on a certain building

app = HouseApp()
app.run()