from imports import*

dictmapping = {"aa": 0}

def read_fasta(seq, idealseq, part_length, thresh_percent):
    for seq_record in SeqIO.parse(seq, "fasta"):
        #print(seq_record.id)
        #print(repr(seq_record.seq))
        #print(len(seq_record))
        #print(seq_record.description)
        seq_name_id = seq_record.name
        n = len(seq_record)
        seqbases=seq_record.seq
        features = dynamic_part_calculation(seqbases, idealseq, part_length, thresh_percent)
    return features, seq_name_id

def dynamic_match(ideal, seq, part_length, thresh_percent):
    comp_seq = seq.complement()
    dc = 0
    cc = 0
    doc = 0
    count = 0
    try:
        for i in range(part_length):
            if ideal[i] == seq[i]:
                dc += 1
            if ideal[i] == comp_seq[i]:
                cc += 1
        doc = dc + cc
        dcpercent = (dc / part_length) * 100
        ccpercent = (cc / part_length) * 100
        docpercent = (doc / part_length) * 100

        if dcpercent >= thresh_percent:
            count = 3
        elif ccpercent >= thresh_percent:
            count = 2
        elif docpercent >= thresh_percent:
            count = 1
        else:
            count = 0
    except Exception as e:
        print(e)
    return count

def dynamic_part_calculation(seqbases, template, part_length, thresh_percent):
    n = len(seqbases)
    t = len(template)
    feature = np.array([])
    try:
        for i in range(0, n-t):
            subseq = seqbases[i:i + t]
            decnum = 0
            decposcount = 0
            for j in range(0, t, part_length):
                idealpart = template[j:j + part_length]
                seqpart = seqbases[i + j: i + j + part_length]
                if idealpart + seqpart not in dictmapping:
                    count = dynamic_match(idealpart, seqpart, part_length, thresh_percent)
                    dictmapping[idealpart + seqpart] = count
                else:
                    count = dictmapping[idealpart + seqpart]

                if count == 3:
                    decnum = decnum + 2 ^ decposcount
                    decnum = decnum + 2 ^ (decposcount + 1)
                elif count == 2:
                    decnum = decnum + 2 ^ (decposcount + 1)
                elif count == 1:
                    decnum = decnum + 2 ^ decposcount
            feature = np.append(feature, decnum)
    except Exception as e:
        print(e)

    return feature

def read_sequence_names(target_directory):
    res = []
    # Iterate directory
    for file in os.listdir(target_directory):
        # check only text files
        if file.endswith('.fasta'):
            res.append(file)
    return res


def to_lower_triangular(matrix):
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if j > i:
                matrix[i][j] = 0

def to_lower_triangular_del(matrix):
    n = len(matrix)
    for i in range(n):
        del matrix[i][i+1:n]

def template_generation(k):
    id_seq = ''
    bases = 'AG'
    for i in range(k+1):
        for j in range(len(bases)):
            for k in range(i):
               id_seq = id_seq + bases[j]
    return id_seq

class DynamicTM:
    def read_fas1(self,dataset_name,k_len,thresh_percent,method):
        try:
            # Get the current directory
            target_directory = dataset_name

            # List all files in the target directory
            # files = os.listdir(target_directory)
            sequence_dic = read_sequence_names(target_directory)

            #idealseq = 'AGAAGGAAAGGGAAAAGGGGAAAAAGGGGG'
            idealseq = template_generation(k_len)
            part_length = 10
            feature_size = int(pow(2, (len(idealseq)/k_len)*2))
            hist_redcution_rate = 1
            descriptor = np.zeros((len(sequence_dic), int(feature_size/hist_redcution_rate)))
            i = 0
            sequence_name_dic = []
            for seq in sequence_dic:
                seq_features, seq_name_id = read_fasta(target_directory+"/"+seq, idealseq, k_len, thresh_percent)
                sequence_name_dic.append(seq_name_id)
                #descriptor[0][0:] = np.array(seq_features)
                hist = np.histogram(seq_features, int(feature_size/hist_redcution_rate))
                descriptor[i] = hist[0]
                i = i+1
            # Step 2: Distance Calculation
            # Compute pairwise distances based on the feature vectors

            distances = pairwise_distances(descriptor, metric='euclidean')

            # Create a DistanceMatrix object from the distances
            distances2dlist = distances.tolist()
            to_lower_triangular_del(distances2dlist)

            # Convert to lower triangular format using numpy.tril()
            #distances2d_lower_trian = np.tril(distances2dlist)
            #distances2d_lt_2dlist = distances2d_lower_trian.tolist()
            #to_lower_triangular(distances2dlist)
            dm = DistanceMatrix(sequence_name_dic, matrix=distances2dlist)

            # Step 3: Phylogenetic Tree Construction
            # Build the phylogenetic tree using the DistanceTreeConstructor
            constructor = DistanceTreeConstructor()
            if method.lower() == 'upgma':
                tree = constructor.upgma(dm)
            elif method.lower() == 'nj':
                tree = constructor.nj(dm)
            else:
                raise ValueError(f"Unknown tree construction method: {method}")

            # Visualize the tree
            #Phylo.draw(tree)
            # Render the tree in a HTML format
            #tree_gen = Phylo.draw_ascii(tree)

        except Exception as e:
            print(e)
        handle=StringIO()
        Phylo.write(tree,handle,'newick')
        newic=handle.getvalue()
        handle.close()
        return tree,newic



