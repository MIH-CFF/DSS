/**
 * API client for DSS backend
 */

export interface SequenceFile {
  filename: string;
  content: string; // base64 encoded
}

export interface AnalysisRequest {
  files: SequenceFile[];
  method: string;
  parameters?: Record<string, any>;
}

export interface AnalysisResponse {
  success: boolean;
  message: string;
  tree_newick?: string;
  distance_matrix?: number[][];
  sequence_names: string[];
  metadata: Record<string, any>;
  execution_time?: number;
}

export interface MethodInfo {
  name: string;
  description: string;
  parameters: Record<string, any>;
}

export interface SequenceData {
  name: string;
  sequence: string;
  length: number;
}

class DSSApiClient {
  private baseUrl: string;

  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async getMethods(): Promise<MethodInfo[]> {
    const response = await fetch(`${this.baseUrl}/methods`);
    if (!response.ok) {
      throw new Error(`Failed to fetch methods: ${response.statusText}`);
    }
    return response.json();
  }

  async getMethodInfo(methodName: string): Promise<MethodInfo> {
    const response = await fetch(`${this.baseUrl}/methods/${methodName}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch method info: ${response.statusText}`);
    }
    return response.json();
  }

  async uploadAndParse(files: File[]): Promise<SequenceData[]> {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    const response = await fetch(`${this.baseUrl}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Failed to upload files: ${response.statusText}`);
    }
    return response.json();
  }

  async analyzeSequences(request: AnalysisRequest): Promise<AnalysisResponse> {
    const response = await fetch(`${this.baseUrl}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `Analysis failed: ${response.statusText}`);
    }
    return response.json();
  }

  async healthCheck(): Promise<{ status: string; message: string }> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }
    return response.json();
  }

  // Utility method to convert File to base64
  async fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const result = reader.result as string;
        // Remove data:*;base64, prefix
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = reject;
    });
  }

  // Helper method to prepare files for analysis
  async prepareFilesForAnalysis(files: File[]): Promise<SequenceFile[]> {
    const sequenceFiles: SequenceFile[] = [];
    
    for (const file of files) {
      const base64Content = await this.fileToBase64(file);
      sequenceFiles.push({
        filename: file.name,
        content: base64Content,
      });
    }
    
    return sequenceFiles;
  }
}

export const dssApi = new DSSApiClient();