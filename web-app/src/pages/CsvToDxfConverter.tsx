import React, { useState } from 'react';
import { FileSpreadsheet, FileText, Download, Upload, CheckCircle2 } from 'lucide-react';
import { useToast } from '../components/Toast';

const CsvToDxfConverter: React.FC = () => {
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [converting, setConverting] = useState(false);
  const [conversionResult, setConversionResult] = useState<{ success: boolean; message: string; dxfFile?: string } | null>(null);
  const [convertedBlob, setConvertedBlob] = useState<Blob | null>(null);
  const { showToast } = useToast();

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.name.endsWith('.csv')) {
        setCsvFile(file);
        setConversionResult(null);
      } else {
        showToast('请选择有效的CSV文件', 'error');
      }
    }
  };

  const handleConvert = async () => {
    if (!csvFile) {
      showToast('请先选择CSV文件', 'error');
      return;
    }

    setConverting(true);
    
    try {
      // 创建FormData对象
      const formData = new FormData();
      formData.append('file', csvFile);
      
      // 调用后端API进行转换
      const response = await fetch('http://localhost:8000/api/csv/to/dxf', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('转换失败，请检查文件格式');
      }
      
      // 处理转换结果
      const blob = await response.blob();
      setConvertedBlob(blob);
      
      // 转换成功后自动触发下载
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${csvFile.name.replace('.csv', '')}_converted.dxf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      setConversionResult({
          success: true,
          message: 'CSV文件转换成功！',
          dxfFile: `${csvFile.name.replace('.csv', '')}_converted.dxf`
        });
        showToast('CSV文件转换成功！', 'success');
      } catch (error) {
        setConversionResult({
          success: false,
          message: error instanceof Error ? error.message : '转换失败，请检查文件格式'
        });
        showToast(error instanceof Error ? error.message : '转换失败，请检查文件格式', 'error');
      } finally {
        setConverting(false);
      }
  };

  const handleDownload = () => {
    if (conversionResult?.success && conversionResult.dxfFile && convertedBlob) {
      try {
        const url = window.URL.createObjectURL(convertedBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = conversionResult.dxfFile;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        showToast(`下载文件: ${conversionResult.dxfFile}`, 'success');
      } catch (error) {
        console.error('Download error:', error);
        showToast('下载失败，请重试', 'error');
      }
    } else {
      showToast('没有可下载的文件', 'error');
    }
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* 页面标题和说明 */}
      <div className="text-center">
        <div className="flex items-center justify-center space-x-3 mb-3">
          <FileSpreadsheet className="h-10 w-10 text-indigo-600" />
          <h1 className="text-3xl font-bold text-gray-900">CSV 转 DXF 转换器</h1>
        </div>
        <p className="text-gray-600 max-w-2xl mx-auto">
          上传CSV文件，将其转换为DXF格式以便在CAD软件中使用
        </p>
      </div>

      {/* 文件上传区域 */}
      <div className="card p-8 bg-gradient-to-br from-white to-gray-50 shadow-lg">
        <h2 className="text-xl font-semibold text-gray-900 mb-6 text-center">选择CSV文件</h2>
        
        <div 
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300 ${csvFile ? 'border-green-400 bg-green-50' : 'border-gray-300 hover:border-indigo-400'}`}
          onDragOver={(e) => {
            e.preventDefault();
            e.currentTarget.classList.add('border-indigo-500', 'bg-indigo-50');
          }}
          onDragLeave={(e) => {
            e.preventDefault();
            e.currentTarget.classList.remove('border-indigo-500', 'bg-indigo-50');
          }}
          onDrop={(e) => {
            e.preventDefault();
            e.currentTarget.classList.remove('border-indigo-500', 'bg-indigo-50');
            
            const file = e.dataTransfer.files?.[0];
            if (file && file.name.endsWith('.csv')) {
              // 创建一个虚拟的input元素来触发handleFileSelect
              const input = document.createElement('input');
              input.type = 'file';
              input.files = e.dataTransfer.files;
              
              // 调用handleFileSelect
              handleFileSelect({ target: input } as React.ChangeEvent<HTMLInputElement>);
            } else {
              showToast('请选择有效的CSV文件', 'error');
            }
          }}
        >
          <input
            type="file"
            id="csv-file"
            accept=".csv"
            onChange={handleFileSelect}
            className="hidden"
          />
          
          {!csvFile ? (
            <label htmlFor="csv-file" className="cursor-pointer">
              <Upload className="h-16 w-16 text-gray-400 mx-auto mb-4 transition-colors hover:text-indigo-600" />
              <p className="text-gray-700 mb-2 text-lg font-medium">点击或拖拽CSV文件到此处</p>
              <p className="text-sm text-gray-500">支持 .csv 格式文件</p>
              <div className="mt-6 inline-block px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">
                选择文件
              </div>
            </label>
          ) : (
            <div className="space-y-4">
              <CheckCircle2 className="h-16 w-16 text-green-500 mx-auto" />
              <div>
                <p className="font-semibold text-gray-900 text-lg">{csvFile.name}</p>
                <p className="text-sm text-gray-500">
                  文件大小: {(csvFile.size / 1024).toFixed(2)} KB
                </p>
              </div>
              <div className="flex justify-center space-x-4">
                <button
                  onClick={() => setCsvFile(null)}
                  className="px-4 py-2 text-red-600 hover:text-red-700 text-sm border border-red-200 rounded-lg hover:bg-red-50 transition-colors"
                >
                  重新选择
                </button>
                <button
                  onClick={handleConvert}
                  disabled={converting}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-70"
                >
                  {converting ? (
                    <span className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                      <span>转换中...</span>
                    </span>
                  ) : (
                    <span className="flex items-center space-x-2">
                      <FileSpreadsheet className="h-4 w-4" />
                      <span>开始转换</span>
                    </span>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 转换结果 */}
      {conversionResult && (
        <div className={`card p-8 shadow-lg ${conversionResult.success ? 'bg-gradient-to-br from-white to-green-50' : 'bg-gradient-to-br from-white to-red-50'}`}>
          <div className="flex items-start space-x-4">
            {conversionResult.success ? (
              <CheckCircle2 className="h-10 w-10 text-green-500 mt-1 flex-shrink-0" />
            ) : (
              <div className="h-10 w-10 text-red-500 mt-1 flex-shrink-0 flex items-center justify-center rounded-full bg-red-100">
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            )}
            <div className="flex-1">
              <h3 className="text-xl font-semibold text-gray-900 mb-2">转换结果</h3>
              <p className={`text-lg ${conversionResult.success ? 'text-green-700' : 'text-red-700'}`}>
                {conversionResult.message}
              </p>
              {conversionResult.success && conversionResult.dxfFile && (
                <div className="mt-6">
                  <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="text-sm text-gray-500">转换后的文件</p>
                        <p className="text-gray-900 font-medium">{conversionResult.dxfFile}</p>
                      </div>
                      <button 
                        onClick={handleDownload}
                        className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        <Download className="h-4 w-4" />
                        <span>下载DXF</span>
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CsvToDxfConverter;