# Thesis for the [UCLA MAS program](https://master.stat.ucla.edu/)

Chair: Professor Yingnian Wu

## Summary
Using Deep Learning to predict genre using lyrics, cover art, and musical features. Various Deep Learning models are applied to input data. A GBM is used to take outputs from the 3 base models in order to provide a final output.

## How to Run
### Install Necessary Libraries and Components
1. Install files found in requirements.txt
2. In order to run models efficiently, use a GPU

### Download Data
1. Download [musiXmatch Lyrics Dataset](http://millionsongdataset.com/musixmatch/#getting) for lyrics
2. Recreate db using instructions found [here](https://github.com/lalinsky/mbdata). Run nbs/processing/Generate Cover Art Data.ipynb to download cover art
3.  Download [Million Song Dataset](https://aws.amazon.com/datasets/million-song-dataset/) for musical features
4. Download [TU Wien MSD Allmusic Style Dataset(MASD)](http://www.ifs.tuwien.ac.at/mir/msd/download.html#groundtruth) for labels

### Processing
1. Run nbs/processing/Generate Lyrics Data.ipynb
2. Run Generate Musical Arrays (60s samples).ipynb
3. Run Generate Test and Train Splits.ipynb

### Model
1. Run nbs/base_models.ipynb
2. Run nbs/ensemble.ipynb

### Results
| src   | accuracy | precision | recall | f1    |
|-------|----------|-----------|--------|-------|
| gbm   | 0.287    | 0.28      | 0.287  | 0.277 |
| lyr   | 0.225    | 0.198     | 0.225  | 0.194 |
| img   | 0.186    | 0.16      | 0.186  | 0.166 |
| music | 0.285    | 0.278     | 0.285  | 0.255 |