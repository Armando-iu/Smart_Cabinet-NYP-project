import os

# this was used because i used multiple datasets from different places. Hence the labels required for the models need to be changed using this program

# folder path
dir_path = r'C:\Users\arman\Iot sys proj 1\IndomieSeg.v4i.yolov9\valid\labels'
count = 0
# Iterate directory
for path in os.listdir(dir_path):
    # find absolute directory of your file
    file_loc = os.path.join(dir_path , path) 
    fp = open(file_loc, "r")

    to_replace = "1" + fp.read()[1:] # change to label 1
    
    print(fp.read())
    print(f"path {path}")

    # rewrite directory
    fp = open(file_loc , 'w')
    fp.write(to_replace)
    fp.close()

    # to check how many files were changed. for debugging
    if os.path.isfile(os.path.join(dir_path, path)):
        count += 1
print('File count:', count) 