import torch
import torch.nn as nn
import torch.optim as optimization
import torchvision.models as models
import torchvision.transforms as transforms
from torchvision.utils import save_image
from PIL import Image
import streamlit as st

# Define device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Define preprocessing
img_size = 512 if torch.cuda.is_available() else 128
loader = transforms.Compose([
    transforms.Resize(img_size),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

def load_img(path):
    img = Image.open(path).convert("RGB")  # Convert to RGB to handle alpha channel
    img = loader(img).unsqueeze(0)
    return img.to(device)

def gram_matrix(input, c, h, w):
    input = input.view(c, -1)
    G = torch.mm(input, input.t())
    return G


def get_content_loss(target, content):
    return torch.mean((target - content) ** 2)

def get_style_loss(target, style):
    _, c, h, w = target.size()
    G = gram_matrix(target, c, h, w)
    S = gram_matrix(style, c, h, w)
    return torch.mean((G - S) ** 2) / (c * h * w)

# Define VGG class
class VGG(nn.Module):
    def __init__(self):
        super(VGG, self).__init__()
        self.select_features = ['0', '5', '10', '19', '28']
        self.vgg = models.vgg19(pretrained=True).features

    def forward(self, x):
        features = []
        for name, layer in self.vgg._modules.items():
            x = layer(x)
            if name in self.select_features:
                features.append(x)
        return features

# Load the VGG model
vgg = VGG().to(device).eval()

# Streamlit UI
st.title("Neural Style Transfer")
st.sidebar.header("Settings")

# Upload content and style images
content_file = st.sidebar.file_uploader("Upload Content Image", type=["png", "jpg", "jpeg"])
style_file = st.sidebar.file_uploader("Upload Style Image", type=["png", "jpg", "jpeg"])

# Weight settings
alpha = st.sidebar.slider("Content Weight (alpha)", 0.1, 10.0, 1.0)
beta = st.sidebar.slider("Style Weight (beta)", 1000, 20000, 10000)
steps = st.sidebar.slider("Number of Steps", 100, 2000, 1000)

if content_file and style_file:
    # Load images
    content_img = load_img(content_file)
    style_img = load_img(style_file)
    target_img = content_img.clone().requires_grad_(True)

    # Display images
    st.image([content_file, style_file], caption=["Content Image", "Style Image"], width=300)

    # Optimizer
    optimizer = optimization.Adam([target_img], lr=0.01)

    # Style transfer process
    progress = st.progress(0)
        # Store intermediate images for grid display
    intermediate_images = []
    for step in range(steps):
        target_feature = vgg(target_img)
        content_feature = vgg(content_img)
        style_feature = vgg(style_img)

        style_loss = 0
        content_loss = 0
        for target, content, style in zip(target_feature, content_feature, style_feature):
            content_loss += get_content_loss(target, content)
            style_loss += get_style_loss(target, style)

        total_loss = alpha * content_loss + beta * style_loss
        optimizer.zero_grad()
        total_loss.backward()
        optimizer.step()

        # Save intermediate images every 100 steps
        if step % 100 == 0:
            intermediate_img = target_img.detach().cpu().squeeze().permute(1, 2, 0).clamp(0, 1).numpy()
            intermediate_images.append((step, intermediate_img))
            progress.progress(int(100 * step / steps))

    # Display the grid of intermediate images
    num_cols = 3  # Number of columns in the grid
    cols = st.columns(num_cols)
    for idx, (step, img) in enumerate(intermediate_images):
        col = cols[idx % num_cols]
        with col:
            st.image(img, caption=f"Step {step}", use_container_width=True)

    # Save and display the final image
    denormalization = transforms.Normalize((-2.12, -2.04, -1.80), (4.37, 4.46, 4.44))
    result = target_img.clone().squeeze()
    result = denormalization(result).clamp(0, 1)
    save_image(result, "result.png")

    st.image("result.png", caption="Final Stylized Image", use_container_width=True)
    st.download_button("Download Image", data=open("result.png", "rb").read(), file_name="stylized_image.png", mime="image/png")
