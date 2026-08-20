import os
import zipfile
import pandas as pd
import cv2
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision.models as models
import torchvision.transforms as transforms
import wandb
from tqdm import tqdm

# ==========================================
# 1. Kaggle
# ==========================================
os.environ['KAGGLE_USERNAME'] = "YOUR_KAGGLE_USERNAME"
os.environ['KAGGLE_KEY'] = "YOUR_KAGGLE_KEY"

if not os.path.exists("train_images"):
    print("Data from kaggle ⏳")
    os.system("kaggle competitions download -c aptos2019-blindness-detection")
    
    print("Unzip ")
    with zipfile.ZipFile("aptos2019-blindness-detection.zip", 'r') as zip_ref:
        zip_ref.extractall(".")
    print("Dataset done! ✅")

# ==========================================
# 2. Dataset & DataLoader
# ==========================================
def crop_and_resize(image_path, size=224):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 7, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)
        img = img[y:y+h, x:x+w]
    return cv2.resize(img, (size, size))

class RetinaDataset(Dataset):
    def __init__(self, csv_file, img_dir, transform=None):
        self.data = pd.read_csv(csv_file)
        self.img_dir = img_dir
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        img_name = os.path.join(self.img_dir, f"{self.data.iloc[idx, 0]}.png")
        image = crop_and_resize(img_name)
        label = self.data.iloc[idx, 1]
        if self.transform:
            image = self.transform(image)
        return image, label

transform = transforms.Compose([transforms.ToTensor()])
train_dataset = RetinaDataset(csv_file="train.csv", img_dir="train_images", transform=transform)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=4)

# ==========================================
# 3. W&B
# ==========================================
wandb.login()

#!!!!!!!!!! Token !!!!!!!!!!
wandb.init(
    project="retina-ai-diagnosis",
    name="resnet18-france-server",
    config={"learning_rate": 0.001, "epochs": 20, "batch_size": 32}
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Training on: {device}")

model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
model.fc = nn.Linear(model.fc.in_features, 5)
model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=wandb.config.learning_rate)

# ==========================================
# 4. Training Loop
# ==========================================
epochs = wandb.config.epochs
print("Starting ..; ")

for epoch in range(epochs):
    model.train()
    running_loss, correct, total = 0.0, 0, 0
    
    for images, labels in tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}"):
        images, labels = images.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        
    epoch_loss = running_loss / len(train_loader)
    epoch_acc = correct / total
    
    wandb.log({"epoch": epoch + 1, "train_loss": epoch_loss, "train_accuracy": epoch_acc})

torch.save(model.state_dict(), 'model_weights_20ep.pth')
wandb.save('model_weights_20ep.pth')
wandb.finish()
print("Training done!")