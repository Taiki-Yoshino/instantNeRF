
# NeRF and InstantNGP implementation using inline-MLP in Slang.
UC San Diego CSE Early Research Scholars Program in 2023-24  
Team: Taiki Yoshino, David Choi, Rick Rodness, Hayden Kwok  
Advised By: Ravi Ramamoorthi, Tzu Mao Li

Abstract: 
*View synthesis models such as NeRF and InstantNGP are usually implemented in either PyTorch or custom CUDA kernels. Each option carries tradeoffs. Choosing PyTorch facilitates easier development due to its auto-differentiation capabilities, though it may suffer from slower memory access which can reduce performance. On the other hand, using CUDA can enhance performance, but the absence of auto differentiation has you writing a few thousand lines of code for the backward pass. Recently, a programming language named Slang has been gaining attention as a new option, that claims to offer both high performance and ease of development with auto differentiation. ​In this project, we implemented two view synthesis algorithms, NeRF and InstantNGP, in Slang and compared their performance with implementations in PyTorch. The results indicated that the Slang implementations were faster in the forward pass but slower in the backward pass. Our analysis identified that the bottleneck was the code generated by Slang's auto-differentiation. In future work, we want to explore which of our specific implementations may have complicated the computational graph, as well as how to better optimize the backward path in Slang.*

## Setup
Install [PyTorch's CUDA](https://pytorch.org/get-started/locally/) and [slangpy/slangtorch](https://shader-slang.com/slang/user-guide/a1-02-slangpy.html). 


```bash
#Installation of slangtorch
pip install slangtorch　
```


## Running the Code

```bash
python run.py <model>     
# Replace <model> with either ('slang','torch','slanghash','torchhash')
```

## Rendered Scenes

<div style="display: inline-block; width: 30%;">
    <img src="results/gifs/slanghash.gif" alt="slang" width="100%" />
    <p style="text-align: center;">Slang NeRF</p>
</div>
<div style="display: inline-block; width: 30%;">
    <img src="results/gifs/torchhash.gif" alt="torch" width="100%" />
    <p style="text-align: center;">PyTorch NeRF</p>
</div>

## Performance
|            |      NeRF （PyTorch）    |      NeRF   （SLAN）       | InstantNGP　（PyTorch） | InstantNGP　（SLANG）  |
|:----------:|:--------------:|:--------------:|:----------:|:----------:|
|  Fwd (ms)  |      2.60      |     0.657      |    9.91    |    8.42    |
| Fwd + Bwd  (ms)  |      4.61      |     19.3       |   43.1     |    54.6    |
|    PSNR    |      21.4      |     20.1       |   22.7     |    22.8    |


## Repo  

```bash
InstantNeRF/
├── data/                      # Datasets
│   └── dataset.npz/           
├── models/                    # MLP models
│   ├── slang_mlp    
│   │   └── ...                # slang inline-MLP files
│   └── troch_mlp
│       └──mlp.py              # Pytorch MLP
├── result/                    
├── trainers/                  
│   ├── slang_trainer.py       # train with slang_mlp
│   ├── torch_trainer.py       # train with torch_mlp
│   ├── slanghash_trainer.py   # train with slang_mlp with hash encoding 
│   └── torchhash_trainer.py   # train with torch_mlp with hash encoding 
├── utils/                     
│   ├── hashencoder            
│   ├── data_loader.py         # load & pre-process data
│   ├── encoder.py             
│   ├── rendering_utils.py    
│   └── save_image.py
└── run.py                      # main calls one of the trainer
```

## Reference
1. NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis
https://arxiv.org/abs/2003.08934
2. Instant Neural Graphics Primitives with a Multiresolution Hash Encoding  
https://nvlabs.github.io/instant-ngp/
3. Inline-MLP in Slang  
https://github.com/shader-slang/slang-python/tree/main/examples/inline-mlp-example
