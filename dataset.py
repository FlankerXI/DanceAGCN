import os
import torch
import random
import numpy as np

from skeleton_sequence import SkeletonSequence

class DanceDataset(torch.utils.data.Dataset):
    def __init__(self, holder, data_in='raw', bez_degree=None, window=10, for_animation=False):
        self.holder = holder  # the object created in dataset_holder.py
        self.data_in = data_in
        self.bez_degree = bez_degree
        self.window = window
        self.for_animation = for_animation

    def __len__(self):
        return self.holder.n_samples

    def get_music_skel_seq(self, item):
        return None, SkeletonSequence(None)  # to be overridden

    def __getitem__(self, item):
        # music, skel_seq = self.get_music_skel_seq(item)
        skel_seq = self.get_music_skel_seq(item)
        metadata = skel_seq.metadata
        label = metadata['label']
        dance = self.get_dance_data(skel_seq)

        if self.for_animation:
            # DX: Modified _data member here just for visualization
            skel_seq._data = dance
            return dance, label, metadata, skel_seq
        
        return dance, label, metadata
        
    def get_dance_data(self, skel_sequence):
        if self.data_in == 'raw':
            return skel_sequence.get_raw_data(as_is=True)
        
        elif self.data_in == 'raw+bcurve':
            return skel_sequence.get_raw_plus_bcurve_data(self.bez_degree, padding_size=self.holder.seq_length)
        
        elif self.data_in.split('+',1)[0] == 'bcurve':
            # frames_list_path = skel_sequence.metadata['filename'].replace('.json', '.npy')
            frames_list_path = skel_sequence.metadata['filename'].split('.',1)[0]+'.npy'
            frames_list_path = self.holder.data_path.rsplit('/', 1)[0] + '/frames_list/' + frames_list_path
            frames_list = np.load(frames_list_path).tolist()
            
            target_length = 1800 if self.holder.source == 'dancerevolution' else 2878
            
            b, _, outliers= skel_sequence.get_bezier_skeleton(order=self.bez_degree, body=0, window=self.window, overlap=4, target_length=None,
                                                    frames_list=frames_list, bounds=(0, target_length-1))
            return b.astype('<f4')
        else:
            raise ValueError(f'Cannot deal with this data input: {self.data_in}')


class DanceRevolutionDataset(DanceDataset):
    def __init__(self, holder, data_in='raw', bez_degree=None, window=10, for_animation=False):
        super().__init__(holder, data_in, bez_degree=bez_degree, window=window, for_animation=for_animation)

    def get_music_skel_seq(self, item):
        # music = self.holder.music_array[item]
        skel_seq = self.holder.skeletons[item]
        # return music, skel_seq
        return skel_seq
