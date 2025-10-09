"""
FastAPI application for DSS REST API
"""
import time
import traceback
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import base64

from src.core.analysis_service import AnalysisService
from src.core.plugin_loader import plugin_loader
from src.core.interfaces import MethodConfig
from src.api.models import (
    AnalysisRequest, AnalysisResponse, MethodInfoResponse, 
    StatusResponse, SequenceDataResponse
)
from src.api.sequence_loader import InMemorySequenceLoader


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    # Load plugins
    plugin_loader.load_all_plugins()
    
    app = FastAPI(
        title="DSS - DNA Sequence Similarity API",
        description="REST API for DNA sequence similarity analysis with multiple algorithms",
        version="2.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize services
    analysis_service = AnalysisService()
    sequence_loader = InMemorySequenceLoader()
    
    @app.get("/", response_model=StatusResponse)
    async def root():
        """Root endpoint"""
        return StatusResponse(
            status="success",
            message="DSS API is running",
            data={
                "version": "2.0.0",
                "available_methods": analysis_service.get_available_methods()
            }
        )
    
    @app.get("/methods", response_model=List[MethodInfoResponse])
    async def get_methods():
        """Get available analysis methods"""
        methods = []
        for method_name in analysis_service.get_available_methods():
            config = analysis_service.get_method_config(method_name)
            if config:
                methods.append(MethodInfoResponse(
                    name=config.name,
                    description=config.description,
                    parameters=config.parameters
                ))
        return methods
    
    @app.get("/methods/{method_name}", response_model=MethodInfoResponse)
    async def get_method_info(method_name: str):
        """Get information about a specific method"""
        config = analysis_service.get_method_config(method_name)
        if not config:
            raise HTTPException(status_code=404, detail=f"Method '{method_name}' not found")
        
        return MethodInfoResponse(
            name=config.name,
            description=config.description,
            parameters=config.parameters
        )
    
    @app.post("/analyze", response_model=AnalysisResponse)
    async def analyze_sequences(request: AnalysisRequest):
        """Analyze DNA sequences using the specified method"""
        try:
            start_time = time.time()
            
            # Validate method
            if request.method not in analysis_service.get_available_methods():
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid method: {request.method}"
                )
            
            # Load sequences from uploaded files
            files_data = [(f.filename, f.content) for f in request.files]
            sequences = sequence_loader.load_from_files(files_data)
            
            if not sequences:
                raise HTTPException(
                    status_code=400,
                    detail="No valid sequences found in uploaded files"
                )
            
            # Get method configuration and merge with request parameters
            default_config = analysis_service.get_method_config(request.method)
            if not default_config:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to get configuration for method: {request.method}"
                )
            
            # Merge default parameters with request parameters
            merged_params = {**default_config.parameters, **request.parameters}
            config = MethodConfig(
                name=default_config.name,
                parameters=merged_params,
                description=default_config.description
            )
            
            # Run analysis
            result = analysis_service.analyze_sequences(sequences, request.method, config)
            
            execution_time = time.time() - start_time
            
            # Convert distance matrix to list format
            distance_matrix = result.distance_matrix.tolist() if result.distance_matrix is not None else None
            
            return AnalysisResponse(
                success=True,
                message="Analysis completed successfully",
                tree_newick=result.newick,
                distance_matrix=distance_matrix,
                sequence_names=result.sequence_names,
                metadata=result.metadata,
                execution_time=execution_time
            )
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Analysis error: {str(e)}")
            print(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed: {str(e)}"
            )
    
    @app.post("/upload", response_model=List[SequenceDataResponse])
    async def upload_and_parse(files: List[UploadFile] = File(...)):
        """Upload and parse sequence files to preview sequences"""
        try:
            files_data = []
            for file in files:
                content = await file.read()
                base64_content = base64.b64encode(content).decode('utf-8')
                files_data.append((file.filename, base64_content))
            
            sequences = sequence_loader.load_from_files(files_data)
            
            return [
                SequenceDataResponse(
                    name=seq.name,
                    sequence=seq.sequence[:100] + "..." if len(seq.sequence) > 100 else seq.sequence,
                    length=len(seq.sequence)
                )
                for seq in sequences
            ]
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse uploaded files: {str(e)}"
            )
    
    @app.get("/health", response_model=StatusResponse)
    async def health_check():
        """Health check endpoint"""
        return StatusResponse(
            status="healthy",
            message="API is operational",
            data={
                "loaded_plugins": len(analysis_service.get_available_methods())
            }
        )
    
    return app


# For direct running
app = create_app()