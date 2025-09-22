from imports import*

def ThreeBaseState(target, ideal, winLen):
    """
    Calculate similarity between target and ideal sequences (3-base version)
    
    Parameters:
    target (str): Target DNA sequence
    ideal (str): Ideal DNA sequence
    winLen (int): Window length
    
    Returns:
    int: Count of matching bases
    """
    cont = 0
    for st in range(winLen):
        if target[st] == ideal[st]:
            cont += 1
    return cont

def FourBaseState(target, ideal, winLen):
    """
    Calculate similarity between target and ideal sequences (4-base version)
    
    Parameters:
    target (str): Target DNA sequence
    ideal (str): Ideal DNA sequence
    winLen (int): Window length
    
    Returns:
    int: Similarity score (0-3)
    """
    count = 0
    for st in range(winLen):
        if target[st] == ideal[st]:
            count += 1
    
    if count == 4 or count == 3:
        return 3
    elif count == 2:
        return 2
    elif count == 1:
        return 1
    else:
        return 0

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

def FourBaseWithCompState(target, ideal, winLen):
    """
    Calculate similarity considering both forward and complement matches
    
    Parameters:
    target (str): Target DNA sequence
    ideal (str): Ideal DNA sequence
    winLen (int): Window length
    
    Returns:
    int: Similarity score (0-3)
    """
    fcont = 0
    ccont = 0
    
    for st in range(winLen):
        if target[st] == ideal[st]:
            fcont += 1
        
        z = complement(target[st])
        if z == ideal[st]:
            ccont += 1
    
    if fcont == winLen:
        return 3
    elif ccont == winLen:
        return 2
    elif fcont == 2 or ccont == 2:
        return 1
    else:
        return 0

def ThreeBaseSeqDiff(sequence, idealSeq, partition, baseLength):
    """
    Calculate sequence difference features using a sliding window approach
    
    Parameters:
    sequence (str): DNA sequence
    idealSeq (str): Ideal reference sequence
    partition (int): Number of partitions
    baseLength (int): Base length for comparison
    
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
        for j in range(0, idealSeqLength, baseLength):
            # Calculate similarity for right side sequences
            if (i + j + baseLength) <= w:
                count = FourBaseState(
                    sequence[i+j:i+j+baseLength], 
                    idealSeq[j:j+baseLength], 
                    baseLength
                )
                
                if count == 1:
                    decNum += 1 * (2 ** t)
                elif count == 2:
                    decNum += 1 * (2 ** (t + 1))
                elif count == 3:
                    decNum += 1 * (2 ** t)
                    decNum += 1 * (2 ** (t + 1))
                
                t += 2
        
        distances[i] = decNum
    
    # Partition and create histogram features
    step = w // partition
    binSize = 2 ** ((idealSeqLength // baseLength) * 2)
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

class PTM:
    """
    Class to process sequences using the PTM method and generate phylogenetic trees.
    """
    def __init__(self):
        self.descriptors = {}

    
    def generate_ideal_sequence(self, k):
        """
        Generate an ideal sequence based on k value
        
        Parameters:
        k (int): Parameter to determine sequence length
        
        Returns:
        str: Generated ideal sequence
        """
        # Simple implementation - can be customized
        bases = "ATCG"
        ideal_seq = ""
        
        # Create a pattern-based ideal sequence
        for i in range(k):
            pattern = bases[i % 4] * (i + 1)
            ideal_seq += pattern
        
        return ideal_seq
    
    def process_sequences(self, directory, partition=1, baseLength=4,ideal_seq=None):
        """
        Process all FASTA files in a directory and generate PTM descriptors.
        
        Parameters:
        directory (str): Path to directory containing FASTA files
        partition (int): Number of partitions for feature extraction
        baseLength (int): Base length for comparison
        ideal_seq (str): Ideal reference sequence (optional)
        
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
                sequence = str(seq_record.seq).upper()
                sequence_names.append(seq_record.id)
                
                # Generate PTM features
                descriptor = ThreeBaseSeqDiff(sequence, ideal_seq, partition, baseLength)
                descriptors.append(descriptor)
                
        return np.array(descriptors), sequence_names
    
    def generate_tree(self, directory, partition=1, baseLength=4, ideal_seq=None,
                      metric='euclidean', method='upgma'):
        """
        Generate a phylogenetic tree from sequences in a directory.
        
        Parameters:
        directory (str): Path to directory containing FASTA files
        partition (int): Number of partitions for feature extraction
        baseLength (int): Base length for comparison
        ideal_seq (str): Ideal reference sequence (optional)
        metric (str): Distance metric to use
        method (str): Tree construction method
        
        Returns:
        Bio.Phylo.BaseTree.Tree: Phylogenetic tree
        """
        # Process sequences to get descriptors
        descriptors, sequence_names = self.process_sequences(
            directory, partition, baseLength,ideal_seq
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

    def run(self,directory, partition,baseLength,method):
        # Measure memory usage
        # start_memory = get_memory_usage()
        # start_time = time.time()
        
        # Process sequences and generate tree
        self.ideal_sequence = "ATCGAATTCCGGAAAATTTTCCCCGGGG"  # Default ideal sequence
        try: 
            if os.path.exists(directory):
                tree = self.generate_tree(
                    directory=directory, 
                    partition=partition, 
                    baseLength=baseLength, 
                    ideal_seq=self.ideal_sequence,
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
                # plt.title('UPGMA Distance Tree')
                # plt.savefig('ptm_phylogenetic_tree.png', dpi=300, bbox_inches='tight')
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