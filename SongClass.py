import scipy.signal
import imagehash
import os
from scipy.io import wavfile
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import (binary_erosion,generate_binary_structure,iterate_structure)
import matplotlib.mlab as mlab
import logging
import pandas as pd
from scipy.spatial.distance import hamming


logging.basicConfig(filename='log.log',level=logging.DEBUG)
all_songs_data = []
processed_songs = []

class SongClass:

    logging.info('Song Loaded')
    def __init__(self,idx,is_mix=False):

        srate,song_data = wavfile.read(all_songs_data[idx])
        self.song_name = str(all_songs_data[idx])
        self.song_name = self.song_name[11:-6]
        logging.info(self.song_name[11:-6])
        self.srate = 44100
        if is_mix:
            self.song_data = song_data[0:int(float(self.srate * 60.0))]
            #
        else:
            self.song_data = song_data[0:int(float(self.srate * 60.0)),0]
        wavfile.write('tryit.wav',self.srate,self.song_data)
        self.window_size = 4096
        self.amp_min = 20
        self.default_overlap_ratio = 0.2
        self.connect_mask = 2
        self.peak_neighbourhood_size = 20
        self.fan_value = 20 # how much it can be paired with others
        #logging.info(self.processed_songs)

    def fingerprint(self,update=False):
        self.data = mlab.specgram(self.song_data, Fs=self.srate, NFFT=self.window_size, window=mlab.window_hanning,
                                  noverlap=int(self.window_size * self.default_overlap_ratio))[0]
        self.imag = self.data
        self.data = 10 * np.log10(self.data, out=np.zeros_like(self.data), where=(self.data != 0))
        self.data[self.data== -np.inf] =0

        #logging.info(self.local_maxima)

        if update:
            self.local_maxima = self.get_maxima(update=True)
        else:
            self.local_maxima = self.get_maxima()
        self.c = 0
        self.features = Image.open('temp.png')
        self.c += 1
        self.hashed = imagehash.phash(self.features)
        logging.info(self.hashed)
        if update==False:
            processed_songs.append((self.song_name, self.hashed))


    def generate_spectrogram(self):
        pass


    def get_maxima(self,update=False):
        '''
        1)generate a mask that has a square shape for better performance
        '''
        struct = generate_binary_structure(2,self.connect_mask)
        '''
        2) peak_neighborhood is the number of cells around an amplitude peak in spectrogram 
        to be considered as a specrtal peak 
        '''
        neighbor = iterate_structure(struct,self.peak_neighbourhood_size)

        '''
        3) apply a max filter with the filter mask we created on my song data with the output shape of the struct with the peak neighborhood size 
        that we can specify, for better accuracy i chose 20 points to be considered.  
        '''
        local_max = maximum_filter(self.data,footprint=neighbor) == self.data
        '''
        4) remove background by first identifying the points in my data where the values are zero, by a boolean mask on my data(XOR) and then we can 
        remove it using the scipy function binary_erosion
        '''
        background = (self.data ==0)
        eroded_background = binary_erosion(background,structure=neighbor,border_value=1)
        '''
        5) now we have the data of the local maximas when we remove the background from the output of the max filter
         we can just extract the peaks of and their frequencies & time points. and we can filter the peaks by flattening
        '''
        detect_peaks = local_max != eroded_background
        amps = self.data[detect_peaks]
        freqs,times = np.where(detect_peaks)
        amps = amps.flatten()
        '''
        6) we can finally get the indices for the frequency and time with np.where 
        i specified the amp.min to be 20 which is the minimum amplitude that we can consider
        when getting peaks
        '''
        filter_idxs =np.where(amps>self.amp_min)
        self.frequencies_filter = freqs[filter_idxs]
        self.times_filter = times[filter_idxs]
        fig,ax = plt.subplots()
        ax.axis('off')
        #ax.set_position([0,0,1,1])
        '''
        if update:
            frex,tims,pwr=scipy.signal.spectrogram(self.song_data,fs=self.srate, nfft=self.window_size)
            plt.pcolormesh(tims,frex,pwr,vmin=0,vmax=9)
            fig.patch.set_alpha(0.)
            ax.patch.set_alpha(0.)
            plt.savefig(f"Spectrograms/{self.song_name}_spectrogram.png",transparent=True)
        else:
        '''
        self.imag = mlab.specgram(self.song_data, Fs=self.srate, NFFT=self.window_size, window=mlab.window_hanning,
                                  noverlap=int(self.window_size * self.default_overlap_ratio))[0]

        plt.imshow(self.imag)
        #ax.scatter(self.times_filter, self.frequencies_filter)
        plt.gca().invert_yaxis()
        plt.show()
        #fig.patch.set_alpha(0.)
        #ax.patch.set_alpha(0.)
        plt.savefig('temp.png')
        #plt.savefig(f"Spectrograms/Features/{self.song_name}_locmax.png", transparent=True)
        return list(zip(self.frequencies_filter,self.times_filter))


    def mix(self,song2,slider):
        slider = slider/100
        mixed = np.average([self.song_data,song2.song_data],axis=0,weights=[slider, (1-slider)])
        wavfile.write('mixed.wav', 44100, mixed)
        all_songs_data.append('mixed.wav')
        self.mixed_song = SongClass(-1, is_mix=True)
        self.mixed_song.fingerprint(update=True)
        all_songs_data.pop(-1)
        difference = []
        #print(len(SongClass.processed_songs))
        similarity_output = []
        for i in range(len(processed_songs)):
            #difference.append(1-hamming(str(processed_songs[i][1]) - str(self.mixed_song.hashed))*len(str(self.mixed_song.hashed)))
            # difference.append(SequenceMatcher(None,str(mixed_song.hashed),str(SongClass.processed_songs[i][1])).ratio()*100)
            difference.append((1 - (processed_songs[i][1] - self.mixed_song.hashed) / 64.0) * 100)
        # difference = weight(difference)
        for i in range(len(difference)):
            # j=3*i
            similarity_output.append((processed_songs[i][0][7:],processed_songs[i][0][0:7], difference[i]))
        print('list',similarity_output)
        df = pd.DataFrame(similarity_output, columns=['Song', 'Group', 'Similarity'])
        df = df.sort_values(by='Similarity', ascending=False)
        print(df)
        return df
        # similarity = [y for x in (SongClass.processed_songs[0],difference) for y in x]
        # print('similarity list: ',similarity)


def weight(list):
    x=[]
    print('inside weight: ',len(list))
    for i in range(0,len(list),3):
        x.append(np.average([list[i],list[i+1],list[i+2]],weights=[1,1,1]))
    print(len(x),'len of x')
    return x


