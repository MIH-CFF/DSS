import React, { useState, useEffect } from 'react';
import {
  Card,
  Upload,
  Select,
  Button,
  Typography,
  Space,
  Alert,
  Spin,
  Table,
  Collapse,
  Form,
  InputNumber,
  message,
  Divider,
} from 'antd';
import { InboxOutlined, PlayCircleOutlined } from '@ant-design/icons';
import type { UploadProps, UploadFile } from 'antd';
import { dssApi, MethodInfo, SequenceData, AnalysisResponse } from '../services/dssApi';
import PhylogeneticTree from '../components/PhylogeneticTree';

const { Title, Text, Paragraph } = Typography;
const { Dragger } = Upload;
const { Panel } = Collapse;

export const DSAAnalysis: React.FC = () => {
  const [methods, setMethods] = useState<MethodInfo[]>([]);
  const [selectedMethod, setSelectedMethod] = useState<string>('');
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [sequenceData, setSequenceData] = useState<SequenceData[]>([]);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState<AnalysisResponse | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    loadMethods();
  }, []);

  const loadMethods = async () => {
    try {
      setLoading(true);
      const methodList = await dssApi.getMethods();
      setMethods(methodList);
      if (methodList.length > 0) {
        setSelectedMethod(methodList[0].name);
      }
    } catch (error) {
      message.error('Failed to load analysis methods');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const uploadProps: UploadProps = {
    multiple: true,
    accept: '.fasta,.fa,.fas,.zip',
    beforeUpload: (file) => {
      setUploadedFiles(prev => [...prev, file]);
      return false; // Prevent auto upload
    },
    onRemove: (file: UploadFile) => {
      setUploadedFiles(prev => prev.filter(f => f.name !== file.name));
      setSequenceData([]);
    },
  };

  const parseUploadedFiles = async () => {
    if (uploadedFiles.length === 0) {
      message.warning('Please upload sequence files first');
      return;
    }

    try {
      setLoading(true);
      const sequences = await dssApi.uploadAndParse(uploadedFiles);
      setSequenceData(sequences);
      message.success(`Parsed ${sequences.length} sequences`);
    } catch (error) {
      message.error('Failed to parse uploaded files');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const runAnalysis = async () => {
    if (uploadedFiles.length === 0) {
      message.warning('Please upload sequence files first');
      return;
    }

    if (!selectedMethod) {
      message.warning('Please select an analysis method');
      return;
    }

    try {
      setAnalyzing(true);
      const formValues = form.getFieldsValue();
      
      // Prepare files for analysis
      const sequenceFiles = await dssApi.prepareFilesForAnalysis(uploadedFiles);
      
      const analysisRequest = {
        files: sequenceFiles,
        method: selectedMethod,
        parameters: formValues,
      };

      const result = await dssApi.analyzeSequences(analysisRequest);
      setResults(result);
      message.success(`Analysis completed in ${result.execution_time?.toFixed(2)}s`);
    } catch (error) {
      message.error('Analysis failed: ' + (error as Error).message);
      console.error(error);
    } finally {
      setAnalyzing(false);
    }
  };

  const selectedMethodInfo = methods.find(m => m.name === selectedMethod);

  const sequenceColumns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Length',
      dataIndex: 'length',
      key: 'length',
    },
    {
      title: 'Sequence Preview',
      dataIndex: 'sequence',
      key: 'sequence',
      render: (text: string) => (
        <Text code style={{ fontSize: '12px' }}>
          {text.length > 50 ? text.substring(0, 50) + '...' : text}
        </Text>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <Title level={2}>DNA Sequence Analysis</Title>
      <Paragraph>
        Upload FASTA files or ZIP archives containing sequence data for phylogenetic analysis.
      </Paragraph>

      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* File Upload */}
        <Card title="Upload Sequence Files">
          <Dragger {...uploadProps}>
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">Click or drag files to upload</p>
            <p className="ant-upload-hint">
              Support for FASTA files (.fasta, .fa, .fas) and ZIP archives
            </p>
          </Dragger>
          
          {uploadedFiles.length > 0 && (
            <div style={{ marginTop: '16px' }}>
              <Button onClick={parseUploadedFiles} loading={loading}>
                Parse Files ({uploadedFiles.length} uploaded)
              </Button>
            </div>
          )}
        </Card>

        {/* Sequence Preview */}
        {sequenceData.length > 0 && (
          <Card title={`Parsed Sequences (${sequenceData.length})`}>
            <Table
              dataSource={sequenceData}
              columns={sequenceColumns}
              rowKey="name"
              size="small"
              pagination={{ pageSize: 10 }}
            />
          </Card>
        )}

        {/* Method Selection */}
        <Card title="Analysis Configuration">
          <Form form={form} layout="vertical">
            <Form.Item label="Analysis Method">
              <Select
                value={selectedMethod}
                onChange={setSelectedMethod}
                loading={loading}
                style={{ width: '100%' }}
              >
                {methods.map(method => (
                  <Select.Option key={method.name} value={method.name}>
                    {method.name}
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>

            {selectedMethodInfo && (
              <Collapse>
                <Panel header="Method Parameters" key="params">
                  <Paragraph>{selectedMethodInfo.description}</Paragraph>
                  <Divider />
                  
                  {Object.entries(selectedMethodInfo.parameters).map(([key, defaultValue]) => (
                    <Form.Item
                      key={key}
                      name={key}
                      label={key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      initialValue={defaultValue}
                    >
                      {typeof defaultValue === 'number' ? (
                        <InputNumber style={{ width: '100%' }} />
                      ) : (
                        <Select style={{ width: '100%' }}>
                          <Select.Option value={defaultValue}>{String(defaultValue)}</Select.Option>
                        </Select>
                      )}
                    </Form.Item>
                  ))}
                </Panel>
              </Collapse>
            )}
          </Form>
        </Card>

        {/* Analysis Button */}
        <Card>
          <Button
            type="primary"
            size="large"
            icon={<PlayCircleOutlined />}
            onClick={runAnalysis}
            loading={analyzing}
            disabled={uploadedFiles.length === 0}
            style={{ width: '100%' }}
          >
            {analyzing ? 'Running Analysis...' : 'Start Analysis'}
          </Button>
        </Card>

        {/* Results */}
        {results && (
          <Card title="Analysis Results">
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <Alert
                message="Analysis Completed Successfully"
                description={`Processed ${results.sequence_names.length} sequences in ${results.execution_time?.toFixed(2)}s`}
                type="success"
                showIcon
              />
              
              {/* Phylogenetic Tree Visualization */}
              {results.tree_newick && (
                <PhylogeneticTree
                  data={results.tree_newick}
                  width={800}
                  height={500}
                  showControls={true}
                  direction="LR"
                  onNodeClick={(node) => {
                    console.log('Node clicked:', node);
                    message.info(`Selected: ${node.label || node.id}`);
                  }}
                />
              )}
              
              <Collapse>
                <Panel header="Phylogenetic Tree (Newick Format)" key="tree">
                  <Text code style={{ fontSize: '12px', wordBreak: 'break-all' }}>
                    {results.tree_newick}
                  </Text>
                </Panel>
                
                <Panel header="Distance Matrix" key="matrix">
                  <Table
                    dataSource={results.distance_matrix?.map((row, i) => ({
                      key: i,
                      sequence: results.sequence_names[i],
                      ...row.reduce((acc, val, j) => ({ ...acc, [`dist_${j}`]: val.toFixed(4) }), {}),
                    }))}
                    columns={[
                      { title: 'Sequence', dataIndex: 'sequence', key: 'sequence', fixed: 'left' },
                      ...results.sequence_names.map((name, i) => ({
                        title: name,
                        dataIndex: `dist_${i}`,
                        key: `dist_${i}`,
                        width: 100,
                      })),
                    ]}
                    scroll={{ x: true }}
                    size="small"
                  />
                </Panel>
              </Collapse>
            </Space>
          </Card>
        )}
      </Space>
    </div>
  );
};