import React, { useState } from 'react';
import { Zap, FolderOpen, Download } from 'lucide-react';
import { useToast } from '../components/Toast';

const VfdDesigner: React.FC = () => {
  const [projectName, setProjectName] = useState('');
  const [projectFolder, setProjectFolder] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const { showToast } = useToast();
  const [parameters, setParameters] = useState({
    diameter: '',
    stroke: '',
    force: '',
    damping: ''
  });

  const vfdModels = [
    'VFD-100', 'VFD-150', 'VFD-200', 'VFD-250', 'VFD-300',
    'VFD-350', 'VFD-400', 'VFD-450', 'VFD-500', 'VFD-550'
  ];

  const handleParameterChange = (field: string, value: string) => {
    setParameters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleGenerateDrawings = async () => {
    if (!selectedModel) {
      showToast('请选择产品型号', 'error');
      return;
    }
    
    try {
      // 调用后端API生成图纸
      const response = await fetch('http://localhost:8000/api/vfd/design', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          projectName,
          projectFolder,
          selectedModel,
          parameters
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || '生成图纸失败');
      }
      
      const result = await response.json();
      showToast('粘滞产品图纸生成成功！', 'success');
      console.log('粘滞产品设计结果:', result);
    } catch (error) {
      console.error('生成图纸错误:', error);
      showToast(error instanceof Error ? error.message : '生成图纸失败，请检查网络连接', 'error');
    }
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Zap className="h-8 w-8 text-green-600" />
          <h1 className="text-2xl font-bold text-gray-900">粘滞产品设计</h1>
        </div>
        <div className="flex space-x-3">
          <button className="btn-secondary flex items-center space-x-2">
            <FolderOpen className="h-4 w-4" />
            <span>打开项目</span>
          </button>
          <button 
            className="btn-primary flex items-center space-x-2"
            onClick={handleGenerateDrawings}
          >
            <Download className="h-4 w-4" />
            <span>生成图纸</span>
          </button>
        </div>
      </div>

      {/* 项目信息区域 */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">项目信息</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="form-label">项目名称</label>
            <input
              type="text"
              className="input-field"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="请输入项目名称"
            />
          </div>
          <div>
            <label className="form-label">项目文件夹</label>
            <div className="flex space-x-2">
              <input
                type="text"
                className="input-field flex-1"
                value={projectFolder}
                onChange={(e) => setProjectFolder(e.target.value)}
                placeholder="选择项目保存文件夹"
              />
              <button className="btn-secondary">
                <FolderOpen className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 产品型号选择 */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">产品型号选择</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {vfdModels.map(model => (
            <button
              key={model}
              onClick={() => setSelectedModel(model)}
              className={`p-3 rounded-lg border-2 transition-all duration-200 ${
                selectedModel === model
                  ? 'border-green-500 bg-green-50 text-green-700'
                  : 'border-gray-300 hover:border-green-300'
              }`}
            >
              {model}
            </button>
          ))}
        </div>
        {selectedModel && (
          <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
            <span className="text-green-700 font-medium">
              已选择型号: {selectedModel}
            </span>
          </div>
        )}
      </div>

      {/* 参数配置 */}
      {selectedModel && (
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">参数配置</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="form-label">缸径(mm)</label>
              <input
                type="number"
                className="input-field"
                value={parameters.diameter}
                onChange={(e) => handleParameterChange('diameter', e.target.value)}
                placeholder="输入缸径尺寸"
              />
            </div>
            <div>
              <label className="form-label">行程(mm)</label>
              <input
                type="number"
                className="input-field"
                value={parameters.stroke}
                onChange={(e) => handleParameterChange('stroke', e.target.value)}
                placeholder="输入行程尺寸"
              />
            </div>
            <div>
              <label className="form-label">设计力(kN)</label>
              <input
                type="number"
                className="input-field"
                value={parameters.force}
                onChange={(e) => handleParameterChange('force', e.target.value)}
                placeholder="输入设计力"
              />
            </div>
            <div>
              <label className="form-label">阻尼系数</label>
              <input
                type="number"
                className="input-field"
                value={parameters.damping}
                onChange={(e) => handleParameterChange('damping', e.target.value)}
                placeholder="输入阻尼系数"
              />
            </div>
          </div>
        </div>
      )}

      {/* 预览区域 */}
      {selectedModel && (
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">设计预览</h2>
          <div className="bg-gray-100 rounded-lg p-8 text-center">
            <Zap className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">
              粘滞阻尼器 {selectedModel} 设计预览
            </p>
            <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="font-semibold">缸径:</span> {parameters.diameter || '--'}mm
              </div>
              <div>
                <span className="font-semibold">行程:</span> {parameters.stroke || '--'}mm
              </div>
              <div>
                <span className="font-semibold">设计力:</span> {parameters.force || '--'}kN
              </div>
              <div>
                <span className="font-semibold">阻尼系数:</span> {parameters.damping || '--'}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VfdDesigner;