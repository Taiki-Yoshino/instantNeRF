import torch
import os
import time
from utils.rendering_utils import volume_rendering
from utils.data_loader import DataLoader
from utils.encoder import pos_embed
from utils.save_image import save_images
import numpy as np
from models.torch_mlp.mlp import MLP
from utils.hashencoder.feature_field import FeatureField
torch.cuda.empty_cache()

class TorchHashTrainer:
    def __init__(self):
        self.width, self.height = 256, 256
        self.N_samples = 32
        self.C = 32
        self.device = 'cuda'
        self.model = MLP(self.C, self.C, self.C).to(self.device)
        self.dataset = DataLoader()
        self.bounding_box = self.dataset.get_bbx()
        self.feature_field = FeatureField(features_per_level = 32).cuda()
        self.loss_fn = torch.nn.MSELoss()
        
    def train(self, iters, lr = 5e-3): #5e-3
        self.iters = iters
        optimizer = torch.optim.Adam([ {'params': self.model.parameters()},
                                      {'params': self.feature_field.parameters()},], lr=lr)
        start = time.time()
        for i in range(iters):
            img_i = np.random.randint(100)
            #get train_data
            x, dists, target_image, viewdirs = self.dataset.get_data(img_i)
            #hashencoding
            x = self.normalize_coordinates(x)
            embedded_x = self.feature_field.encode(x)
            #embedded_x = pos_embed(x)[...,:-1]
            viewdirs = (pos_embed(viewdirs)[...,:16]).unsqueeze(2).expand(-1, -1, self.N_samples, -1)
            #MLP and volume rendering
            y_pred = self.model(embedded_x, viewdirs)
            y_pred = volume_rendering(y_pred, dists)
            #Compute loss and psnr
            loss = self.loss_fn(y_pred, target_image)
            psnr = -10. * torch.log(loss) / torch.math.log(10.)
            print(f"Iteration {i}, Loss: {loss.item()}, psnr: {psnr.item()}")
            #optimize MLP params and hashtable
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        end = time.time()
        print('avg training time:', (end - start)/iters)
        
    def render(self, saveimg):
        intermediate_images = []
        target_images = []
        start = time.time()
        test_images = [100,101,102,103,104,105]
        psnrs = []
        for img_i in test_images:
            x, dists, target_image, viewdirs = self.dataset.get_data(img_i)
            x = self.normalize_coordinates(x)
            embedded_x = self.feature_field.encode(x)
            viewdirs = (pos_embed(viewdirs)[...,:16]).unsqueeze(2).expand(-1, -1, self.N_samples, -1)
            y_pred = self.model(embedded_x, viewdirs)
            y_pred = volume_rendering(y_pred, dists)
            loss = self.loss_fn(y_pred, target_image)
            psnr = -10. * torch.log(loss) / torch.math.log(10.)
            print(f"Iteration {img_i}, Loss: {loss.item()}, psnr: {psnr.item()}")
            if(saveimg):
                intermediate_images.append(y_pred.detach().cpu().numpy())
                target_images.append(target_image.detach().cpu().numpy())
                psnrs.append(psnr.detach().cpu())
        end = time.time()
        print('avg rendering time:', (end - start)/len(test_images))
        if(saveimg):
            save_images(target_images, intermediate_images,'torchhash.png', "PyTorch MLP with hashencoding" , self.iters, psnrs)
            
    def normalize_coordinates(self,x):
        min_xyz = torch.tensor(self.bounding_box[0], dtype=x.dtype, device=x.device)
        max_xyz = torch.tensor(self.bounding_box[1], dtype=x.dtype, device=x.device)
        range_xyz = max_xyz - min_xyz
        x_shape = x.shape
        x = x.reshape(-1,3)
        range_xyz[range_xyz == 0] = 1.0
        x = (x - min_xyz)/range_xyz
        x = x.reshape(x_shape)
        return x