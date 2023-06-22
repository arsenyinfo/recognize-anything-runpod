from logging import getLogger

import runpod
import torch
import torchvision.transforms as transforms
from PIL import Image

from b2 import B2Client
from inference_ram import inference as ram_inference
from inference_tag2text import inference as tag2text_inference
from ram.models.ram import ram
from ram.models.tag2text import tag2text_caption
import os


logger = getLogger(__name__)

b2_client = B2Client()


def get_relative_path(x):
    return os.path.join(os.path.dirname(__file__), x)


class CombinedModel:
    def __init__(self):
        logger.info("Loading models")
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tag_model = ram(
            pretrained=get_relative_path('pretrained/ram_swin_large_14m.pth'),
            image_size=384,
            vit='swin_l'
        ).eval().to(self.device)

        self.caption_model = tag2text_caption(pretrained=get_relative_path('pretrained/tag2text_swin_14m.pth'),
                                              vit='swin_b',
                                              delete_tag_index=[127, 2961, 3351, 3265, 3338, 3355, 3359],
                                              image_size=384,
                                              ).eval().to(self.device)
        self.transform = transforms.Compose([
            transforms.Resize((384, 384)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])
        logger.info("Models loaded")

    def get_ram_caption(self, image_file):
        img = Image.open(image_file)
        processed = self.transform(img.convert("RGB")).unsqueeze(0).to(self.device)
        image_file.close()
        tags, _ = ram_inference(processed, self.tag_model)
        _, _, caption = tag2text_inference(processed, self.caption_model, tags)
        return tags, caption


model = CombinedModel()


def handler(job):
    image = job["input"]["image"]
    img_bytes = b2_client.read_file(image)
    tags, caption = model.get_ram_caption(img_bytes)
    return {"tags": tags, "caption": caption}


runpod.serverless.start({"handler": handler})
