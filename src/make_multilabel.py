import os
import cv2
from PIL import Image
import imagehash

data_path_orig = './../data'

tokens = []
with os.scandir(data_path_orig) as entries:
    for entry in entries:
        if entry.is_dir() and entry.name!='src':
            tokens.append(entry.name)

def get_file_in_dir(path, token):
    files =[]
    for filename in os.listdir(path):
        if filename.endswith(token): 
            files.append(filename)
        else:
            continue
    return files

import pickle


def get_video_hashes_be(video_path):
    cap = cv2.VideoCapture(video_path)
    hashes = []
    frame_count_all = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    success, frame = cap.read()
    frame_count = 0
    while cap.isOpened() and success and frame_count<frame_count_all-1:
        if frame_count < 50 or frame_count> frame_count_all-50:
            success, frame = cap.read()
            if not success:
                break
            # Convert frame to PIL Image
            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            # Compute perceptual hash
            hash_value = imagehash.phash(pil_image)
            hashes.append(hash_value)
        else:
            cap.grab()
        
        frame_count += 1
    cap.release()
    return hashes

def get_video_hashes(video_path, frame_interval=2):
    cap = cv2.VideoCapture(video_path)
    hashes = []
    frame_count = 0
    success, frame = cap.read()
    while success:
        if frame_count % frame_interval == 0:
            # Convert frame to PIL Image
            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            pil_image = pil_image.crop((0, 0, 500, 500))
            # Compute perceptual hash
            hash_value = imagehash.phash(pil_image)
            hashes.append(hash_value)
        success, frame = cap.read()
        if not success:
            break
        frame_count += 1
    cap.release()
    return hashes

def compare_hashes(hashes1, hashes2, threshold):
    count = 0
    for i in range(0,len(hashes1)):
        for j in range(0,len(hashes2)):
            if hashes1[i] == hashes2[j]:
                count = count+1  # Found similar frames
                break
        if count/len(hashes1)>threshold: #already surpassed stop comparing
            return count/len(hashes1)
        if (count + len(hashes1)-i)/len(hashes1)< threshold:#no more possible stop comparing
            return count/len(hashes1)
                
    return count/len(hashes1)

# Funzione per caricare un file .pkl
def load_pkl(file_path):
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
    return data

print(len(tokens))
for ii in range(0,len(tokens)):
    
    token = tokens[ii]
        
    print(token)
    folder = os.path.join(data_path_orig,token)
                
    pkl_file = os.path.join(folder,"coarse_info.pkl" ) 
    desc = load_pkl(pkl_file)
        
    count = 0
    new_desc = []
    new_desc.append([desc[0]["info_coarse"]])
    for i in range(1,len(desc)):
        print(i)
        
        hashes_video1 = get_video_hashes(os.path.join(data_path_orig,token, str(i-1) + '.mp4'))
        hashes_video2 = get_video_hashes(os.path.join(data_path_orig,token, str(i) + '.mp4'))
        check = True
        
        if len(hashes_video1)==0 or len(hashes_video2)==0:
            check = False
        # Get the difference in minutes and seconds
        
        threshold=0.4
        if check:
            check2 = compare_hashes(hashes_video1, hashes_video2,threshold)>threshold
       
        if check and check2:
       
            if  "tag" in desc[i]["info_coarse"] :
                new_desc.append("remove")
                continue
            
            if type(new_desc[i-1])==str:
                new_desc[i-1] = [new_desc[i-1]]
                
            new_desc.append(new_desc[i-1] +[desc[i]["info_coarse"]])
            new_desc[i-1] = "remove"
             
        else:
            if "tag" in desc[i]["info_coarse"] :
                new_desc.append("remove")
                continue
            new_desc.append(desc[i]["info_coarse"])
        
    
    clean_desc = {}
    for k in range(0,len(new_desc)):
        
        if type(new_desc[k]) == str:
            if "remove" in new_desc[k]:
                continue
            
        clean_desc[k] = desc[k]
        
        if type(new_desc[k]) == list:
            clean_desc[k]["info_multi"] = new_desc[k]
            continue
        
        clean_desc[k]["info_multi"] = [new_desc[k]]
    
    for k in clean_desc.keys():
        if len(clean_desc[k]["info_multi"])!=1:
            print(len(clean_desc[k]["info_multi"]))
        
    p = os.path.join(folder,"info_multi.pkl")
    with open(p, 'wb') as file:
         pickle.dump(clean_desc, file)
    
    

            
