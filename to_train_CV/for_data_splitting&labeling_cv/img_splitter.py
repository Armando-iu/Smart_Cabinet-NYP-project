import os 
import random 
from PIL import Image

dir_path = r"C:\Users\arman\Iot sys proj 1\food_pics"

all_pics = []
test = []
valid = []
train = []

def folder_maker(name): 
    newpath = dir_path + "\\" + name + r"\images" 
    if os.path.exists(newpath):
        os.remove(dir_path + "\\" + name)
    if not os.path.exists(newpath): # check if folder is made before
        os.makedirs(newpath) # if not make one. Will not make again if it is made

def collate_all_pics(dir_path , all_pics): # to put all the files into a list 
    for path in os.listdir(dir_path): 
        if not os.path.isdir(dir_path + "\\" + path):
            all_pics.append(path)
    return all_pics

def test_val_train_splitter(all_pics): 
    # calculates the amount of pictures for 10% and 80% of the database 
    full_80 = len(all_pics)/100 * 80
    full_10 = len(all_pics)/100 * 10

    # randomly put images into train ,test and split
    for i in range(len(all_pics)):
        pic = random.choice(all_pics)
        all_pics.remove(pic)
        if full_80 > len(train): # train is 80% of the images
            train.append(pic)
        elif full_10 > len(test): # test is 10% of the images
            test.append(pic)
        elif full_10 > len(valid):# validate is 10% of the images
            valid.append(pic)
    return test , valid , train 

def get_var_name(var):
    for name, value in globals().items():
        if value is var:
            return name
        
def save_img_frm_list(pic_list):
    folder_name = get_var_name(pic_list) # to make folder name. 
    for i in pic_list:
        curr_img_path = dir_path + "\\"  + i
        img = Image.open(curr_img_path)
        save_path = dir_path + "\\" + folder_name + r"\images" + "\\" + i 
        img.save(save_path)

def dupe_checker(test , valid , train):
    # used for debugging: if there are duplicate pictures directories in 2 or more list
    for i in test:
        for x in train:
            if i == x:
                print("dupe founded")
                return True
        for y in valid:
            if i == y:
                print("dupe founded")
                return True

    for i in train:
        for x in test:
            if i == x:
                print("dupe founded")
                return True
        for y in valid:
            if i == y:
                print("dupe founded")
                return True

    for i in valid:
        for x in test:
            if i == x:
                print("dupe founded")
                return True
        for y in test:
            if i == y:
                print("dupe founded")
                return True
    return False

folder_maker("valid")
folder_maker("test")
folder_maker("train")

all_pics = collate_all_pics(dir_path , all_pics)

print(all_pics)

test , valid , train = test_val_train_splitter(all_pics) # dont change the variable names because of below 

# these arguements must be named so. Because they take the variable's name and name the folder that.
# so if the arguements passed is "none" the folder will be called "none"
save_img_frm_list(test)
save_img_frm_list(valid)
save_img_frm_list(train)