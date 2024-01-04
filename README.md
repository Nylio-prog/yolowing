### REQUIREMENTS

Install cuda 11.8 following this video :

https://www.youtube.com/watch?v=r7Am-ZGMef8

If you don't see your GPU used for training or inference after correctly installing cuda, it's likely that you didn't install the right cuda version with pytorch.

<br>

### WORKFLOW

First the data is preprocessed. The first step consists in counting the different bird species and pseudo-randomly selecting a maximum of 100 videos per species for each year. However we kept the year 2021 for testing with a maximum of 50 videos per species. Each video contains about 200 images. The selected videos are copied into a folder and the data dictionary is stored in filtered_species_dict.json (key:video_path, value:{species, is_test_set}). 

We use the YOLOv8 general pretrained model to detect the bounding box of the birds. However, since the model doesn't always recognize the bird accurately, it sometimes predicts another animal. Therefore, by merging all pretrained animals classes into one called birds and using the manual annotation from Poids Plume's database file, we can create a dataset with the right bounding boxes and the right bird species. There will be 3 folders: train, validation and test, each containing image files and label files. 

We can then train the model on this dataset to accurately recognize boxes and also recognize the bird species with given parameters.

<br>

### DATASET

Private dataset containing videos of birds.

In our case, to see some statistics about our dataset, we can run :

```
python database_statistics.py --db-file /path/to/db/file/tsv > statistics/statistics_log.txt
```

<br>

### HOW TO REPRODUCE THE TRAINING ON THE SERVER

Clone the repository with a minimum storage capacity of 15 Gb. 

Once you have the videos directory which contains the videos of the birds, you can call these functions :

```
bash start_env.sh

python preprocess_and_copy_downloaded_data.py -i path/to/videos/directory

python create_dataset.py

python train_model.py
```

You should have the best weights at train_and_validation/yolov8_train/weights/best.pt alongside all the generated metrics and images at train_and_validation/yolov8_train. 

To run test evaluation run this in the command line: 

```
yolo detect val model=path/to/best.pt split='test' 
```

<br>

### REAL-TIME SPECIES PREDICTION 

If your GPU can't run Cuda 11.7 it will take a longer time. 

To predict a video, do this :

```
python main.py -i path/to/video/file -m path/to/best/pt
```

Example:

```
python main.py -i input_files/piou.mp4 -m train_and_validation/yolov8_trained_without_2021/weights/best.pt
```
