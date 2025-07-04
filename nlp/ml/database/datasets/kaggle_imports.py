import kagglehub

# Download latest version
# path = kagglehub.dataset_download("hrmello/brazilian-portuguese-hatespeech-dataset")
path = kagglehub.dataset_download("fredericods/ptbr-sentiment-analysis-datasets")

print("Path to dataset files:", path)