import numpy as np
import os
import matplotlib.pyplot as plt
from Bio import Phylo, SeqIO
from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor
from sklearn.metrics import pairwise_distances
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QFileDialog, QRadioButton, 
                            QSpinBox, QMessageBox, QFrame, QButtonGroup)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
import warnings
warnings.filterwarnings("ignore")
from imports import *
def CGR_K_Mer(sequence):
    """
    Calculate the CGR coordinates for a given k-mer sequence.
    
    Parameters:
    sequence (str): DNA sequence string
    
    Returns:
    tuple: (lx, ly) coordinates in the CGR space
    """
    z = len(sequence)
    lx, ly = 1, 1
    
    for i in range(z):
        if i == 0:
            nuec_base = sequence[-1]  # Last character in sequence
            if nuec_base == 'A':
                lx, ly = 1, 1
            elif nuec_base == 'G':
                lx, ly = 2, 1
            elif nuec_base == 'C':
                lx, ly = 1, 2
            elif nuec_base == 'T':
                lx, ly = 2, 2
        else:
            baseInterval = 2**i / 2
            nuec_base = sequence[z-i-1]  # Reverse order processing
            
            if nuec_base == 'G':
                lx += baseInterval
            elif nuec_base == 'C':
                ly += baseInterval
            elif nuec_base == 'T':
                lx += baseInterval
                ly += baseInterval
                
    return int(lx-1), int(ly-1)  # Convert to 0-indexed coordinates

def CGRImageKmerCount(sequence, kmer):
    """
    Generate a CGR image matrix for a given sequence and k-mer length.
    
    Parameters:
    sequence (str): DNA sequence string
    kmer (int): Length of k-mers to consider
    
    Returns:
    numpy.ndarray: 2D array representing the CGR image
    """
    seqLength = len(sequence)
    
    # Matrix size estimation and assign with zero
    dimension = 2**kmer
    image = np.zeros((dimension, dimension), dtype=np.uint16)
    
    for i in range(seqLength - kmer + 1):
        kmerSeq = sequence[i:i+kmer]
        # CGR Matrix position calculation
        lx, ly = CGR_K_Mer(kmerSeq)
        # Image generation from counting
        if lx < dimension and ly < dimension:  # Ensure within bounds
            image[ly, lx] += 1
            
    return image

def LBP256(image):
    """
    Calculate Local Binary Pattern (LBP) features for an image.
    
    Parameters:
    image (numpy.ndarray): Input image
    
    Returns:
    numpy.ndarray: LBP feature vector of length 256
    """
    # Simple implementation - in practice you would use a proper LBP algorithm
    # This is a placeholder that returns a histogram of the image
    hist, _ = np.histogram(image.flatten(), bins=256, range=(0, 255))
    return hist

def CGROriginal(sequence, kmer):
    """
    Generate the original CGR image for a sequence.
    
    Parameters:
    sequence (str): DNA sequence
    kmer (int): k-mer length
    
    Returns:
    numpy.ndarray: CGR image
    """
    return CGRImageKmerCount(sequence, kmer)

def SqrCGRPartition(CgrImage, numOfPartition):
    """
    Partition a CGR image into smaller squares and extract features.
    
    Parameters:
    CgrImage (numpy.ndarray): Input CGR image
    numOfPartition (int): Number of partitions along each dimension
    
    Returns:
    numpy.ndarray: Feature matrix
    """
    h, w = CgrImage.shape
    part_h, part_w = h // numOfPartition, w // numOfPartition
    features = []
    
    for i in range(numOfPartition):
        for j in range(numOfPartition):
            part = CgrImage[i*part_h:(i+1)*part_h, j*part_w:(j+1)*part_w]
            features.extend(part.flatten())
            
    return np.array(features)

class CGR:
    """
    Class to process sequences using CGR and generate phylogenetic trees.
    """
    def __init__(self):
        self.descriptors = {}
        
    def process_sequences(self, directory, kmer):
        """
        Process all FASTA files in a directory and generate CGR descriptors.
        
        Parameters:
        directory (str): Path to directory containing FASTA files
        kmer (int): k-mer length for CGR
        
        Returns:
        tuple: (descriptors, sequence_names)
        """
        descriptors = []
        sequence_names = []
        
        # Get all FASTA files in directory
        fasta_files = [f for f in os.listdir(directory) if f.endswith('.fasta')]
        
        for fasta_file in fasta_files:
            file_path = os.path.join(directory, fasta_file)
            
            # Read sequence from FASTA file
            for seq_record in SeqIO.parse(file_path, "fasta"):
                sequence = str(seq_record.seq)
                sequence_names.append(seq_record.id)
                
                # Generate CGR image
                cgr_image = CGROriginal(sequence, kmer)
                
                # Extract features (using histogram as descriptor)
                descriptor = cgr_image.flatten()
                descriptors.append(descriptor)
                
        return np.array(descriptors), sequence_names
    
    def generate_tree(self,directory, kmer, method):
        """
        Generate a phylogenetic tree from sequences in a directory.
        
        Parameters:
        directory (str): Path to directory containing FASTA files
        kmer (int): k-mer length for CGR
        metric (str): Distance metric to use
        method (str): Tree construction method
        
        Returns:
        Bio.Phylo.BaseTree.Tree: Phylogenetic tree
        """
        metric='euclidean'
        # Process sequences to get descriptors
        descriptors, sequence_names = self.process_sequences(directory,kmer)
        
        # Calculate distance matrix
        distances = pairwise_distances(descriptors, metric=metric)
        
        # Convert to lower triangular format
        n = len(sequence_names)
        dist_matrix = []
        for i in range(n):
            dist_matrix.append(distances[i, :i+1].tolist())
        
        # Create DistanceMatrix object
        dm = DistanceMatrix(sequence_names, matrix=dist_matrix)
        
        # Construct phylogenetic tree
        constructor = DistanceTreeConstructor()
        if method.lower() == 'upgma':
            tree = constructor.upgma(dm)
        elif method.lower() == 'nj':
            tree = constructor.nj(dm)
        else:
            raise ValueError(f"Unknown tree construction method: {method}")
            
        handle=StringIO()
        Phylo.write(tree,handle,'newick')
        newic=handle.getvalue()
        handle.close()
        return tree,newic

