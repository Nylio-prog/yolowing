### REQUIREMENTS

Install cuda 11.8 following this video :

https://www.youtube.com/watch?v=r7Am-ZGMef8

If you don't see your GPU used for training or inference after correctly installing cuda, it's likely that you didn't install the right cuda version with pytorch.

### PROCESS

From COCO dataset, we use the pretrained model of YOLOv8 to detect the bounding box of the birds. However, since the camera doesn't always accurately the bird, the prediction sometimes predicts the wrong animal. Therefore, to create we can merge all animals classes into one called birds and using the manual annotation from Poids Plume, we can create a dataset with the right bounding boxes and the right bird species. We can then train the model on this dataset to accurately recognize boxes and also recognize the bird species.

### DATASET

Private dataset containing videos of birds.

In our case, to see some statistics about our dataset, we can run :

```
python database_statistics.py --db-file db_file.tsv > statistics/statistics_log.txt
```

### ENTIRE PROCEDURE

Once you have the videos directory which contains the videos of the birds from 2021 and before, you can call these functions :

```
python preprocess_and_copy_downloaded_data.py -i path/to/videos

python create_dataset.py

python train_model.py
```

To predict a video, do this after putting the weights best.pt from output_training into the working directory :

```
python main.py -i path/to/video/file -m path/to/best/pt
```
