import React, { useState } from 'react';
import { Table, Upload, Download, Edit, Plus, Trash2 } from 'lucide-react';
import { useToast } from '../components/Toast';

const CsvEditor: React.FC = () => {
  const [csvData, setCsvData] = useState<Array<Record<string, string>>>([]);
  const [headers, setHeaders] = useState<string[]>([]);
  const [editingCell, setEditingCell] = useState<{row: number, col: number} | null>(null);
  const [editingValue, setEditingValue] = useState('');
  const { showToast } = useToast();

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.name.endsWith('.csv')) {
      try {
        // 创建FormData对象
        const formData = new FormData();
        formData.append('file', file);
        
        // 调用后端API解析CSV文件
        const response = await fetch('http://localhost:8000/api/csv/parse', {
          method: 'POST',
          body: formData
        });
        
        if (!response.ok) {
          throw new Error('解析CSV文件失败');
        }
        
        const result = await response.json();
        setCsvData(result.data);
        setHeaders(result.headers);
      } catch (error) {
        showToast(error instanceof Error ? error.message : '解析CSV文件失败', 'error');
      }
    } else {
      showToast('请选择有效的CSV文件', 'error');
    }
  };

  const handleCellEdit = (row: number, col: number, value: string) => {
    setEditingCell({ row, col });
    setEditingValue(value);
  };

  const handleCellSave = () => {
    if (editingCell) {
      const { row, col } = editingCell;
      const header = headers[col];
      const newData = [...csvData];
      newData[row] = { ...newData[row], [header]: editingValue };
      setCsvData(newData);
      setEditingCell(null);
      setEditingValue('');
    }
  };

  const handleAddRow = () => {
    const newRow: Record<string, string> = {};
    headers.forEach(header => {
      newRow[header] = '';
    });
    setCsvData([...csvData, newRow]);
  };

  const handleDeleteRow = (index: number) => {
    const newData = csvData.filter((_, i) => i !== index);
    setCsvData(newData);
  };

  const handleDownload = async () => {
    if (csvData.length === 0) {
      showToast('没有数据可下载', 'error');
      return;
    }
    
    try {
      // 调用后端API保存CSV文件
      const response = await fetch('/api/csv/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          data: csvData,
          headers: headers
        })
      });
      
      if (!response.ok) {
        throw new Error('保存CSV文件失败');
      }
      
      // 处理下载结果
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'edited_csv_file.csv';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      showToast('CSV文件下载成功！', 'success');
    } catch (error) {
      showToast(error instanceof Error ? error.message : '保存CSV文件失败', 'error');
    }
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* 页面标题和说明 */}
      <div className="text-center">
        <div className="flex items-center justify-center space-x-3 mb-3">
          <Table className="h-10 w-10 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">CSV 编辑器</h1>
        </div>
        <p className="text-gray-600 max-w-2xl mx-auto">
          导入CSV文件，在线编辑数据，然后导出保存
        </p>
      </div>

      {/* 文件上传区域 */}
      {csvData.length === 0 && (
        <div className="card p-8 bg-gradient-to-br from-white to-gray-50 shadow-lg">
          <h2 className="text-xl font-semibold text-gray-900 mb-6 text-center">导入CSV文件</h2>
          <div 
            className="border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300 border-gray-300 hover:border-blue-400"
            onDragOver={(e) => {
              e.preventDefault();
              e.currentTarget.classList.add('border-blue-500', 'bg-blue-50');
            }}
            onDragLeave={(e) => {
              e.preventDefault();
              e.currentTarget.classList.remove('border-blue-500', 'bg-blue-50');
            }}
            onDrop={(e) => {
              e.preventDefault();
              e.currentTarget.classList.remove('border-blue-500', 'bg-blue-50');
              
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
            <label htmlFor="csv-file" className="cursor-pointer">
              <Upload className="h-16 w-16 text-gray-400 mx-auto mb-4 transition-colors hover:text-blue-600" />
              <p className="text-gray-700 mb-2 text-lg font-medium">点击或拖拽CSV文件到此处</p>
              <p className="text-sm text-gray-500">支持 .csv 格式文件</p>
              <div className="mt-6 inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                选择文件
              </div>
            </label>
          </div>
        </div>
      )}

      {/* 数据表格 */}
      {csvData.length > 0 && (
        <div className="card p-8 bg-gradient-to-br from-white to-gray-50 shadow-lg">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold text-gray-900">数据编辑</h2>
            <button
              onClick={handleAddRow}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="h-4 w-4" />
              <span>添加行</span>
            </button>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full table-auto bg-white rounded-lg shadow-sm">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 border-b">
                    操作
                  </th>
                  {headers.map((header, index) => (
                    <th key={index} className="px-4 py-3 text-left text-sm font-semibold text-gray-900 border-b">
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {csvData.map((row, rowIndex) => (
                  <tr key={rowIndex} className="hover:bg-gray-50">
                    <td className="px-4 py-3 border-b">
                      <button
                        onClick={() => handleDeleteRow(rowIndex)}
                        className="flex items-center justify-center w-8 h-8 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                    {headers.map((header, colIndex) => (
                      <td key={colIndex} className="px-4 py-3 border-b">
                        {editingCell?.row === rowIndex && editingCell?.col === colIndex ? (
                          <div className="flex space-x-2 items-center">
                            <input
                              type="text"
                              value={editingValue}
                              onChange={(e) => setEditingValue(e.target.value)}
                              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                              autoFocus
                            />
                            <button
                              onClick={handleCellSave}
                              className="px-3 py-1 bg-blue-600 text-white text-xs rounded-lg hover:bg-blue-700 transition-colors"
                            >
                              保存
                            </button>
                            <button
                              onClick={() => setEditingCell(null)}
                              className="px-3 py-1 bg-brb-orange-200 text-gray-700 text-xs rounded-lg hover:bg-brb-orange-300 transition-colors"
                            >
                              取消
                            </button>
                          </div>
                        ) : (
                          <div 
                            className="flex justify-between items-center cursor-pointer group p-1 rounded-md hover:bg-gray-100"
                            onClick={() => handleCellEdit(rowIndex, colIndex, row[header] || '')}
                          >
                            <span>{row[header] || '-'}</span>
                            <Edit className="h-3 w-3 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                          </div>
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {/* 导出按钮 */}
          <div className="mt-6 flex justify-end">
            <button 
              className="flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              onClick={handleDownload}
            >
              <Download className="h-5 w-5" />
              <span>导出CSV</span>
            </button>
          </div>
        </div>
      )}

      {/* 功能说明 */}
      <div className="card p-8 bg-gradient-to-br from-white to-gray-50 shadow-lg">
        <h2 className="text-xl font-semibold text-gray-900 mb-6 text-center">功能说明</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="space-y-3 text-center">
            <div className="flex items-center justify-center space-x-2 mb-2">
              <Upload className="h-6 w-6 text-blue-600" />
              <span className="font-medium text-gray-900">导入数据</span>
            </div>
            <p className="text-sm text-gray-600">支持导入CSV格式文件，自动解析表头和数据</p>
          </div>
          <div className="space-y-3 text-center">
            <div className="flex items-center justify-center space-x-2 mb-2">
              <Edit className="h-6 w-6 text-green-600" />
              <span className="font-medium text-gray-900">在线编辑</span>
            </div>
            <p className="text-sm text-gray-600">支持点击单元格进行编辑，实时保存修改内容</p>
          </div>
          <div className="space-y-3 text-center">
            <div className="flex items-center justify-center space-x-2 mb-2">
              <Download className="h-6 w-6 text-purple-600" />
              <span className="font-medium text-gray-900">导出数据</span>
            </div>
            <p className="text-sm text-gray-600">将编辑后的数据导出为CSV文件，保持格式完整性</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CsvEditor;