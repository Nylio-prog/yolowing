### REQUIREMENTS

Install cuda 11.8 following this video :

https://www.youtube.com/watch?v=r7Am-ZGMef8

### PROCESS

From COCO dataset, we use the pretrained model of YOLOv8 to detect the bounding box of the birds. However, since the camera doesn't always accurately the bird, the prediction sometimes predicts the wrong animal. Therefore, to create we can merge all animals classes into one called birds and using the manual annotation from Poids Plume, we can create a dataset with the right bounding boxes and the right bird species. We can then train the model on this dataset to accurately recognize boxes and also recognize the bird species.

### USEFUL LINKS FOR DATASETS

https://www.kaggle.com/datasets/gpiosenka/birdies
https://snd.gu.se/en/catalogue/dataset/2021-316-1
