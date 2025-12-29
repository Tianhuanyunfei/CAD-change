import React, { useState, useEffect } from 'react';
import { Table, Upload, Download, Edit, Plus, Trash2 } from 'lucide-react';
import { useToast } from '../components/Toast';

// 全局样式重置，确保表格不会影响页面布局
const resetStyles = {
  '*': {
    boxSizing: 'border-box' as const,
  },
  'html, body': {
    overflowX: 'hidden' as const,
    width: '100%',
    margin: 0,
    padding: 0,
  },
};

const CsvEditor: React.FC = () => {
  // 从localStorage加载初始状态
  const loadInitialState = () => {
    try {
      const savedCsvData = localStorage.getItem('csv_editor_data');
      const savedHeaders = localStorage.getItem('csv_editor_headers');
      const savedFileName = localStorage.getItem('csv_editor_filename') || '';
      
      return {
        csvData: savedCsvData ? JSON.parse(savedCsvData) as Array<Record<string, string>> : [],
        headers: savedHeaders ? JSON.parse(savedHeaders) as string[] : [],
        fileName: savedFileName
      };
    } catch (error) {
      console.error('加载CSV编辑器初始状态失败:', error);
      return {
        csvData: [],
        headers: [],
        fileName: ''
      };
    }
  };
  
  const initialState = loadInitialState();
  
  const [csvData, setCsvData] = useState<Array<Record<string, string>>>(initialState.csvData);
  const [headers, setHeaders] = useState<string[]>(initialState.headers);
  const [editingCell, setEditingCell] = useState<{row: number, col: number} | null>(null);
  const [editingValue, setEditingValue] = useState('');
  const [fileName, setFileName] = useState<string>(initialState.fileName);
  const { showToast } = useToast();
  
  // 监听状态变化并保存到localStorage
  useEffect(() => {
    localStorage.setItem('csv_editor_data', JSON.stringify(csvData));
  }, [csvData]);
  
  useEffect(() => {
    localStorage.setItem('csv_editor_headers', JSON.stringify(headers));
  }, [headers]);
  
  useEffect(() => {
    localStorage.setItem('csv_editor_filename', fileName);
  }, [fileName]);

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
        setFileName(file.name);
      } catch (error) {
        showToast(error instanceof Error ? error.message : '解析CSV文件失败', 'error');
      }
    } else {
      showToast('请选择有效的CSV文件', 'error');
    }
  };

  const handleCellEdit = (row: number, col: number, value: string) => {
    // 清除之前的编辑状态
    setEditingCell(null);
    setEditingValue('');
    
    // 立即设置新的编辑状态
    setTimeout(() => {
      console.log('Edit cell:', row, col, value);
      setEditingCell({ row, col });
      setEditingValue(value);
    }, 0);
  };

  const handleCellSave = () => {
    try {
      if (!editingCell) return;
      
      const { row, col } = editingCell;
      
      // 边界检查
      if (row < 0 || row >= csvData.length || col < 0 || col >= headers.length) {
        console.error('Invalid cell coordinates:', { row, col });
        setEditingCell(null);
        setEditingValue('');
        showToast('无效的单元格坐标', 'error');
        return;
      }
      
      const header = headers[col];
      
      if (!header) {
        console.error('Invalid column index:', col);
        setEditingCell(null);
        setEditingValue('');
        showToast('无效的列索引', 'error');
        return;
      }
      
      console.log('Saving cell:', row, col, header, editingValue);
      
      // 使用函数式更新确保获取最新的状态
      setCsvData(prevData => {
        // 创建新的数据数组
        const newData = [...prevData];
        // 创建新的行对象
        const newRow = { ...newData[row] };
        // 更新单元格值
        newRow[header] = editingValue;
        // 替换行
        newData[row] = newRow;
        console.log('Updated data:', newData);
        return newData;
      });
      
      // 清除编辑状态
      setEditingCell(null);
      setEditingValue('');
      
      console.log('Cell saved successfully');
    } catch (error) {
      console.error('Error saving cell:', error);
      setEditingCell(null);
      setEditingValue('');
      showToast('保存单元格数据失败', 'error');
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
    <div className="space-y-4 p-4" style={{ overflowX: 'hidden' }}>
      {/* 顶部工具栏 - 整合标题、文件名和导入导出按钮 */}
      <div className="card p-4 shadow-lg rounded-lg border border-gray-700" style={{ maxWidth: '100%', boxSizing: 'border-box' }}>
        <div className="flex flex-wrap justify-between items-center gap-4">
          {/* 标题 */}
          <div className="flex items-center space-x-2">
            <Table className="h-6 w-6 text-blue-400" />
            <h1 className="text-xl font-bold text-gray-900">CSV 编辑器</h1>
            {/* 文件名 - 仅在文件打开时显示 */}
            {fileName && (
              <p className="text-sm text-gray-400">{fileName}</p>
            )}
          </div>
          
          {/* 导入导出按钮 */}
          <div className="flex space-x-3">
            {/* 导入按钮 */}
            <label htmlFor="csv-file" className="cursor-pointer">
              <div className="flex items-center space-x-1 px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors">
                <Upload className="h-3 w-3" />
                <span>导入</span>
              </div>
            </label>
            <input
              type="file"
              id="csv-file"
              accept=".csv"
              onChange={handleFileSelect}
              className="hidden"
            />
            <input
              type="file"
              id="csv-file-open"
              accept=".csv"
              onChange={handleFileSelect}
              className="hidden"
            />
            
            {/* 导出按钮 - 仅在文件打开时显示 */}
            {csvData.length > 0 && (
              <button 
                className="flex items-center space-x-1 px-4 py-2 bg-purple-600 text-white text-sm rounded hover:bg-purple-700 transition-colors"
                onClick={handleDownload}
              >
                <Download className="h-3 w-3" />
                <span>导出</span>
              </button>
            )}
            
            {/* 添加行按钮 - 仅在文件打开时显示 */}
            {csvData.length > 0 && (
              <button
                onClick={handleAddRow}
                className="flex items-center space-x-1 px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
              >
                <Plus className="h-3 w-3" />
                <span>添加行</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* 内容区域 */}
      <div className="space-y-4">
        {/* 文件上传区域 - 仅在没有CSV文件时显示 */}
        {csvData.length === 0 && (
          <div className="card p-4 shadow-lg rounded-lg border border-gray-700" style={{ maxWidth: '100%', boxSizing: 'border-box' }}>
            <h2 className="text-lg font-semibold text-gray-900 mb-3">导入CSV文件</h2>
            <div 
              className="border-2 border-dashed rounded-lg p-6 text-center transition-all duration-300 border-gray-700 hover:border-blue-500"
              onDragOver={(e) => {
                e.preventDefault();
                e.currentTarget.classList.add('border-blue-500', 'bg-blue-900/20');
              }}
              onDragLeave={(e) => {
                e.preventDefault();
                e.currentTarget.classList.remove('border-blue-500', 'bg-blue-900/20');
              }}
              onDrop={(e) => {
                e.preventDefault();
                e.currentTarget.classList.remove('border-blue-500', 'bg-blue-900/20');
                
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
              <label htmlFor="csv-file" className="cursor-pointer">
                <Upload className="h-10 w-10 text-gray-400 mx-auto mb-3 transition-colors hover:text-blue-400" />
                <p className="text-gray-300 mb-2 text-sm font-medium">点击或拖拽CSV文件到此处</p>
                <p className="text-xs text-gray-500">支持 .csv 格式文件</p>
                <div className="mt-4 inline-block px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors">
                  选择文件
                </div>
              </label>
            </div>
          </div>
        )}
        
        {/* 数据表格 - 仅在有CSV文件时显示 */}
        {csvData.length > 0 && (
          <div className="overflow-x-auto max-h-[calc(100vh-200px)] border border-gray-200 rounded-xl" style={{ maxWidth: 'calc(100vw - 370px)', width: '100%' }}>
            <table className="w-full table-auto border-collapse">
              <colgroup>
                <col style={{minWidth: '3rem', background: 'white'}} />
                <col style={{minWidth: '4rem', background: 'white'}} />
                {headers.map((_, index) => (
                  <col key={index} style={{minWidth: '80px'}} />
                ))}
              </colgroup>
              <thead>
                <tr className="sticky top-0 z-20 relative">
                  {/* 背景覆盖层 */}
                  <th colSpan={headers.length + 2} className="absolute inset-0 bg-blue-500 z-10 pointer-events-none rounded-t-xl"></th>
                  
                  {/* 表头内容 */}
                  <th className="px-3 py-2 text-left text-xs font-semibold text-white border border-blue-600 whitespace-nowrap relative z-30 rounded-tl-xl">
                    #
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-semibold text-white border border-blue-600 whitespace-nowrap relative z-30">
                    操作
                  </th>
                  {headers.map((header, index) => (
                    <th 
                      key={index} 
                      className={`px-3 py-2 text-left text-xs font-semibold text-white border border-blue-600 whitespace-nowrap relative z-30 ${index === headers.length - 1 ? 'rounded-tr-xl' : ''}`}
                    >
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="text-sm">
                {csvData.map((row, rowIndex) => {
                  const rowKey = `row-${rowIndex}`;
                  const isEvenRow = rowIndex % 2 === 0;
                  
                  return (
                    <tr key={rowKey} className={`${isEvenRow ? 'bg-white' : 'bg-gray-50'} hover:bg-blue-50 transition-colors`}>
                      <td className="px-3 py-1.5 border border-gray-200 text-gray-600 whitespace-nowrap font-medium">
                        {rowIndex + 1}
                      </td>
                      <td className="px-3 py-1.5 border border-gray-200 whitespace-nowrap">
                        <button
                          onClick={() => handleDeleteRow(rowIndex)}
                          className="flex items-center justify-center w-6 h-6 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-full transition-colors"
                        >
                          <Trash2 className="h-3 w-3" />
                        </button>
                      </td>
                      {headers.map((header, colIndex) => {
                        const cellKey = `cell-${rowIndex}-${colIndex}`;
                        const cellValue = row[header] || '';
                        
                        // 根据值的内容提供不同的颜色
                        let textColor = 'text-gray-800';
                        if (cellValue.includes('BYLAYER') || cellValue.includes('Continuous')) {
                          textColor = 'text-blue-700';
                        } else if (cellValue.match(/^[0-9.-]+$/)) {
                          textColor = 'text-indigo-700';
                        } else if (cellValue === '') {
                          textColor = 'text-gray-400';
                        }
                        
                        return (
                          <td key={cellKey} className={`px-3 py-1.5 border border-gray-200 ${textColor} truncate`} style={{overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'}}>
                            {editingCell && editingCell.row === rowIndex && editingCell.col === colIndex ? (
                              <div className="flex space-x-0.5 items-center">
                                <input
                                  type="text"
                                  value={editingValue}
                                  onChange={(e) => {
                                    // 使用函数式更新确保获取最新状态
                                    setEditingValue(e.target.value);
                                  }}
                                  className="flex-1 px-1 py-0.5 border border-gray-600 bg-white text-black text-xs rounded focus:ring-1 focus:ring-blue-500 focus:border-transparent"
                                  autoFocus
                                  // 添加事件防抖
                                  onKeyPress={(e) => {
                                    if (e.key === 'Enter') {
                                      handleCellSave();
                                    } else if (e.key === 'Escape') {
                                      setEditingCell(null);
                                      setEditingValue('');
                                    }
                                  }}
                                />
                                <button
                                  onClick={handleCellSave}
                                  className="px-1 py-0.5 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 transition-colors"
                                >
                                  保存
                                </button>
                                <button
                                  onClick={() => setEditingCell(null)}
                                  className="px-1 py-0.5 bg-gray-600 text-white text-xs rounded hover:bg-gray-700 transition-colors"
                                >
                                  取消
                                </button>
                              </div>
                            ) : (
                              <div 
                                className="flex justify-between items-center cursor-pointer p-0.25 rounded hover:bg-gray-700/50 whitespace-nowrap"
                                onDoubleClick={() => handleCellEdit(rowIndex, colIndex, cellValue)}
                              >
                                <span>{cellValue || '-'}</span>
                                <Edit className="h-2.5 w-2.5 text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                              </div>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default CsvEditor;