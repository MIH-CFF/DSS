"""
Adapter for BioPython sequence loading functionality.
"""
import os
from typing import List
from Bio import SeqIO
from src.core.interfaces import ISequenceLoader, SequenceData


class BioPythonSequenceLoader(ISequenceLoader):
    """Adapter for loading sequences using BioPython"""
    
    def supports_format(self, file_path: str) -> bool:
        """Check if this loader supports the given file format"""
        if os.path.isdir(file_path):
            # Check if directory contains FASTA files
            try:
                for file in os.listdir(file_path):
                    if file.lower().endswith('.fasta'):
                        return True
            except:
                pass
            return False
        
        # Check individual file
        return file_path.lower().endswith(('.fasta', '.fa', '.fas'))
    
    def load_sequences(self, source_path: str) -> List[SequenceData]:
        """Load sequences from the given source"""
        sequences = []
        
        if os.path.isdir(source_path):
            # Load from directory
            sequences = self._load_from_directory(source_path)
        elif os.path.isfile(source_path):
            # Load from single file
            sequences = self._load_from_file(source_path)
        else:
            raise ValueError(f"Invalid source path: {source_path}")
        
        return sequences
    
    def _load_from_directory(self, directory_path: str) -> List[SequenceData]:
        """Load all FASTA files from a directory"""
        sequences = []
        
        for filename in os.listdir(directory_path):
            if filename.lower().endswith('.fasta'):
                file_path = os.path.join(directory_path, filename)
                file_sequences = self._load_from_file(file_path)
                sequences.extend(file_sequences)
        
        return sequences
    
    def _load_from_file(self, file_path: str) -> List[SequenceData]:
        """Load sequences from a single FASTA file"""
        sequences = []
        
        try:
            for seq_record in SeqIO.parse(file_path, "fasta"):
                sequence_data = SequenceData(
                    name=seq_record.name or seq_record.id,
                    sequence=str(seq_record.seq),
                    metadata={
                        'id': seq_record.id,
                        'description': seq_record.description,
                        'length': len(seq_record.seq),
                        'source_file': file_path
                    }
                )
                sequences.append(sequence_data)
        except Exception as e:
            raise Exception(f"Failed to parse FASTA file {file_path}: {str(e)}")
        
        return sequences
