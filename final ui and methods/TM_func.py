from imports import*


def complement(a):
    """
    Get complement of a DNA base
    
    Parameters:
    a (str): DNA base
    
    Returns:
    str: Complement base
    """
    if a == 'A':
        return 'T'
    elif a == 'T':
        return 'A'
    elif a == 'C':
        return 'G'
    elif a == 'G':
        return 'C'
    else:
        return 'N'

def SeqDiff(sequence, idealSeq, partition):
    """
    Calculate sequence difference features using binary encoding
    
    Parameters:
    sequence (str): DNA sequence
    idealSeq (str): Ideal reference sequence
    partition (int): Number of partitions
    
    Returns:
    numpy.ndarray: Feature vector
    """
    w = len(sequence)
    distances = np.zeros(w)
    idealSeqLength = len(idealSeq)
    
    # Iterate through the whole sequence
    for i in range(w):
        decNum = 0
        t = 0
        
        # Match full template
        for j in range(idealSeqLength):
            # Calculate similarity for right side sequences
            if (i + idealSeqLength - j) <= w:
                idealSeqBase = idealSeq[idealSeqLength - 1 - j]
                seqBase = sequence[i + idealSeqLength - 1 - j]
                
                if idealSeqBase == 'A':
                    # AA=11, AT=00, AC=01, AG=10
                    if seqBase == 'A':
                        decNum += 1 * (2 ** t)
                        decNum += 1 * (2 ** (t + 1))
                    elif seqBase == 'C':
                        decNum += 1 * (2 ** t)
                    elif seqBase == 'G':
                        decNum += 1 * (2 ** (t + 1))
                
                elif idealSeqBase == 'T':
                    # TA=00, TT=11, TC=01, TG=10
                    if seqBase == 'T':
                        decNum += 1 * (2 ** t)
                        decNum += 1 * (2 ** (t + 1))
                    elif seqBase == 'C':
                        decNum += 1 * (2 ** t)
                    elif seqBase == 'G':
                        decNum += 1 * (2 ** (t + 1))
                
                elif idealSeqBase == 'C':
                    # CA=00, CT=01, CC=11, CG=10
                    if seqBase == 'T':
                        decNum += 1 * (2 ** t)
                    elif seqBase == 'C':
                        decNum += 1 * (2 ** t)
                        decNum += 1 * (2 ** (t + 1))
                    elif seqBase == 'G':
                        decNum += 1 * (2 ** (t + 1))
                
                elif idealSeqBase == 'G':
                    # GA=00, GT=01, GC=10, GG=11
                    if seqBase == 'T':
                        decNum += 1 * (2 ** t)
                    elif seqBase == 'C':
                        decNum += 1 * (2 ** (t + 1))
                    elif seqBase == 'G':
                        decNum += 1 * (2 ** t)
                        decNum += 1 * (2 ** (t + 1))
                
                t += 2
        
        distances[i] = decNum
    
    # Partition and create histogram features
    step = w // partition
    binSize = 2 ** (idealSeqLength * 2)
    binc = np.arange(0, binSize)
    
    distances2D = np.zeros((partition, binSize))
    
    for i in range(partition):
        startPos = i * step
        endPos = (i + 1) * step if i < partition - 1 else w
        
        if startPos < w:
            partition_data = distances[startPos:endPos]
            hist, _ = np.histogram(partition_data, bins=binSize, range=(0, binSize-1))
            distances2D[i, :] = hist
    
    return distances2D.flatten()

class TM:
    """
    Class to process sequences using the TM method and generate phylogenetic trees.
    """
    def __init__(self):
        self.descriptors = {}
        self.ideal_sequences = ["AAAAAATTTTTT"]  # Default ideal sequence
    
    def set_ideal_sequences(self, ideal_seqs):
        """Set the ideal reference sequences"""
        self.ideal_sequences = ideal_seqs
    
    def generate_ideal_sequence(self, k):
        """
        Generate an ideal sequence based on k value
        
        Parameters:
        k (int): Parameter to determine sequence pattern
        
        Returns:
        str: Generated ideal sequence
        """
        # Different patterns based on k value
        if k <= 4:
            return "ATCG"
        elif k <= 6:
            return "AATTCCGG"
        elif k <= 8:
            return "AAAATTTT"
        elif k <= 10:
            return "AAAAAATTTTTT"
        else:
            return "AAAAAAATTTTTTT"
    
    def process_sequences(self, directory, partition=1, ideal_seqs=None):
        """
        Process all FASTA files in a directory and generate TM descriptors.
        
        Parameters:
        directory (str): Path to directory containing FASTA files
        partition (int): Number of partitions for feature extraction
        ideal_seqs (list): List of ideal reference sequences (optional)
        
        Returns:
        tuple: (descriptors, sequence_names)
        """
        if ideal_seqs is None:
            ideal_seqs = self.ideal_sequences
        
        descriptors = []
        sequence_names = []
        
        # Get all FASTA files in directory
        fasta_files = [f for f in os.listdir(directory) if f.endswith('.fasta')]
        
        for fasta_file in fasta_files:
            file_path = os.path.join(directory, fasta_file)
            
            # Read sequence from FASTA file
            for seq_record in SeqIO.parse(file_path, "fasta"):
                sequence = str(seq_record.seq).upper()
                sequence_names.append(seq_record.id)
                
                # Process with each ideal sequence and combine results
                all_features = []
                for ideal_seq in ideal_seqs:
                    features = SeqDiff(sequence, ideal_seq, partition)
                    all_features.append(features)
                
                # Combine features from all ideal sequences
                combined_features = np.concatenate(all_features)
                descriptors.append(combined_features)
                
        return np.array(descriptors), sequence_names
    
    def generate_tree(self, directory, partition=1, ideal_seqs=None, 
                     metric='euclidean', method='upgma'):
        """
        Generate a phylogenetic tree from sequences in a directory.
        
        Parameters:
        directory (str): Path to directory containing FASTA files
        partition (int): Number of partitions for feature extraction
        ideal_seqs (list): List of ideal reference sequences (optional)
        metric (str): Distance metric to use
        method (str): Tree construction method
        
        Returns:
        Bio.Phylo.BaseTree.Tree: Phylogenetic tree
        """
        # Process sequences to get descriptors
        descriptors, sequence_names = self.process_sequences(
            directory, partition, ideal_seqs
        )
        
        # Calculate distance matrix
        if metric == 'spearman':
            # For spearman, we need to use scipy's pdist
            from scipy.stats import rankdata
            # Convert to ranks for spearman correlation
            ranked_data = np.apply_along_axis(rankdata, 1, descriptors)
            distances = pdist(ranked_data, metric='correlation')
        else:
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
            
        return tree

    def run(self,directory,partition,method):
        # Initialize processor
        processor = TM()
        
        # Set ideal sequences (similar to MATLAB examples)
        self.ideal_sequences = ["AAAAAATTTTTT"]
        
        # Measure memory usage
        # start_memory = get_memory_usage()
        # start_time = time.time()
        
        # Process sequences and generate tree
        try:
            if os.path.exists(directory):
                tree = processor.generate_tree(
                    directory, 
                    partition=partition, 
                    ideal_seqs=self.ideal_sequences,
                    metric='euclidean', 
                    method=method
                )
            handle=StringIO()
            Phylo.write(tree,handle,'newick')
            newic=handle.getvalue()
            handle.close()
            return tree,newic
                # Draw the tree
                # plt.figure(figsize=(12, 8))
                # Phylo.draw(tree, do_show=False)
                # plt.title('UPGMA Distance Tree using TM Method')
                # plt.savefig('tm_phylogenetic_tree.png', dpi=300, bbox_inches='tight')
                # plt.show()
                
                # Print tree in Newick format
                # print("Newick format:")
                # print(Phylo.write(tree, format='newick'))
            
        except Exception as e:
            print(f"Error processing sequences: {e}")
        
        # Measure performance
        # end_time = time.time()
        # end_memory = get_memory_usage()
        
        # print(f"Processing time: {end_time - start_time:.2f} seconds")
        # print(f"Memory usage: {(end_memory - start_memory) / (1024 * 1024):.2f} MB")
