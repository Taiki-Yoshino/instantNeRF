# NeRF Studio: https://github.com/nerfstudio-project/nerfstudio/blob/bc9328c7ff70045fce21838122f48ab5201c4ae3/nerfstudio/field_components/encodings.py#L310

import torch
import math
class FeatureField():
    def __init__(self, hashmap_scale=.0001, log2_hashmap_size=19, features_per_level=2, res=1024):
        self.hashtable_size = 2**log2_hashmap_size
        self.features_per_level = features_per_level
        self.res = res
        # Init the hash table
        self.hashtable = torch.rand(size = (self.table_size * 1 * features_per_level)) * 2 - 1 # table_size * levels * features_per_level
        self.hashtable *= hashmap_scale


    #FOR NOW im assuming x.shape = (3)
    def encode(self, x):
        x_scaled = x * self.res

        x_floor = torch.floor(x_scaled).int()
        x_ceil = torch.ceil(x_scaled).int()
        h0 = self.hash(torch.stack((x_floor[0], x_floor[1], x_floor[2]))) #000
        h1 = self.hash(torch.stack((x_ceil[0], x_floor[1], x_floor[2]))) #100
        h2 = self.hash(torch.stack((x_floor[0], x_ceil[1], x_floor[2]))) #010
        h3 = self.hash(torch.stack((x_floor[0], x_floor[1], x_ceil[2]))) #001
        h4 = self.hash(torch.stack((x_ceil[0], x_ceil[1], x_floor[2]))) #110
        h5 = self.hash(torch.stack((x_ceil[0], x_floor[1], x_ceil[2]))) #101
        h6 = self.hash(torch.stack((x_floor[0], x_ceil[1], x_ceil[2]))) #011
        h7 = self.hash(torch.stack((x_ceil[0], x_ceil[1], x_ceil[2]))) #111
        
        # hash all points
        v0 = hashtable[h0]
        v1 = hashtable[h1]
        v2 = hashtable[h2]
        v3 = hashtable[h3]
        v4 = hashtable[h4]
        v5 = hashtable[h5]
        v6 = hashtable[h6]
        v7 = hashtable[h7]

        x_difference = x_scaled - x_floor
        trilinear_interpolation(x_difference, v0, v1, v2, v3, v4, v5, v6, v7)
        
        #for each level
            #x_scaled =  x * gridResolution[level]
            #x_floor
            #x_ceil


            #if course level where (N_l +1^d <= T) the mapping is 1:1
            #else 
                #hash(x_floor)
                #hash(x_ceil)
                
    #assume 1 point
    def hash(self, x):
        prime0 = 1
        prime1 = 2654435761
        prime2 = 805459861
        result = (prime0 * x[0]) ^ (prime1 * x[1]) ^ (prime2 * x[2])
        return result % self.hashtable_size


    # https://en.wikipedia.org/wiki/Trilinear_interpolation
    def trilinear_interpolation(self, p_d, c_000, c_100, c_010, c_001, c_110, c_101, c_011, c_111):
        #interpolate along x
        c_00 = c000 * (1-p_d[0]) + c_100 * p_d[0]
        c_01 = c001 * (1-p_d[0]) + c_101 * p_d[0]
        c_10 = c010 * (1-p_d[0]) + c_110 * p_d[0]
        c_11 = c010 * (1-p_d[0]) + c_111 * p_d[0]

        #interpolate along y
        c_0 = c_00 * (1-p_d[1]) + c_10 * p_d[1]
        c_1 = c_01 * (1-p_d[1]) + c_11 * p_d[1]

        #interpolate along z
        c = c_0 * (1-p_d[2]) + c_1 * p_d[2]

        return c
        
