"""
In-memory sequence loader for API that processes ZIP files without extraction
"""
import zipfile
import io
import base64
from typing import List, Tuple
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from src.core.interfaces import ISequenceLoader, SequenceData


class InMemorySequenceLoader(ISequenceLoader):
    """Loads sequences from in-memory data without file system operations"""
    
    def __init__(self):
        pass
    
    def supports_format(self, file_path: str) -> bool:
        """Check if this loader supports the given file format"""
        supported_extensions = ['.fasta', '.fa', '.fas', '.zip']
        return any(file_path.lower().endswith(ext) for ext in supported_extensions)
    
    def load_sequences(self, source_path: str) -> List[SequenceData]:
        """Load sequences from the given source - not used for in-memory loader"""
        raise NotImplementedError("InMemorySequenceLoader does not support file path loading. Use load_from_files instead.")
    
    def load_from_files(self, files_data: List[Tuple[str, str]]) -> List[SequenceData]:
        """
        Load sequences from list of (filename, base64_content) tuples
        
        Args:
            files_data: List of tuples containing (filename, base64_encoded_content)
            
        Returns:
            List of SequenceData objects
        """
        sequences = []
        
        for filename, base64_content in files_data:
            try:
                if filename.lower().endswith('.zip'):
                    # Handle ZIP file - keep as binary data
                    zip_bytes = base64.b64decode(base64_content)
                    sequences.extend(self._load_from_zip_content(zip_bytes))
                elif filename.lower().endswith(('.fasta', '.fa', '.fas')):
                    # Handle FASTA file - decode to text
                    file_content = base64.b64decode(base64_content).decode('utf-8')
                    sequences.extend(self._load_from_fasta_content(file_content, filename))
                else:
                    # Try to parse as FASTA anyway - decode to text
                    file_content = base64.b64decode(base64_content).decode('utf-8')
                    sequences.extend(self._load_from_fasta_content(file_content, filename))
                    
            except Exception as e:
                print(f"Warning: Failed to load {filename}: {str(e)}")
                continue
        
        return sequences
    
    def _load_from_zip_content(self, zip_bytes: bytes) -> List[SequenceData]:
        """Load sequences from ZIP file content in memory"""
        sequences = []
        
        try:
            with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zip_file:
                for file_info in zip_file.infolist():
                    if file_info.filename.lower().endswith(('.fasta', '.fa', '.fas')):
                        with zip_file.open(file_info) as fasta_file:
                            content = fasta_file.read().decode('utf-8')
                            sequences.extend(self._load_from_fasta_content(content, file_info.filename))
        except Exception as e:
            print(f"Error processing ZIP file: {str(e)}")
        
        return sequences
    
    def _load_from_fasta_content(self, content: str, filename: str) -> List[SequenceData]:
        """Load sequences from FASTA content string"""
        sequences = []
        
        try:
            # Use StringIO to simulate file reading
            fasta_io = io.StringIO(content)
            
            for record in SeqIO.parse(fasta_io, "fasta"):
                # Clean sequence - remove whitespace and convert to uppercase
                clean_sequence = str(record.seq).upper().replace(' ', '').replace('\n', '')
                
                # Use record ID or filename as name
                name = record.id if record.id else filename
                
                sequences.append(SequenceData(
                    name=name,
                    sequence=clean_sequence
                ))
                
        except Exception as e:
            print(f"Error parsing FASTA content from {filename}: {str(e)}")
        
        return sequences
    
    def get_supported_formats(self) -> List[str]:
        """Return supported file formats"""
        return ['.fasta', '.fa', '.fas', '.zip']