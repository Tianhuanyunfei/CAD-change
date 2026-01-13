import React, { useState, useEffect } from 'react';
import { Shield, CheckCircle, AlertTriangle, Download } from 'lucide-react';
import { useToast } from '../components/Toast';

interface BrbStabilityParams {
  id: string;
  designForce: string; // 设计力(kN)
  coreWidth: string; // 芯板宽度(mm)
  coreThickness: string; // 芯板厚度(mm)
  yieldStrength: string; // 屈服强度(MPa)
  length: string; // 支撑长度(mm)
  tubeWidth: string; // 外套管宽度(mm)
  tubeThickness: string; // 外套管厚度(mm)
  concreteStrength: string; // 填充混凝土强度(MPa)
}

interface StabilityResult {
  id: string;
  slendernessRatio: number; // 长细比
  bucklingStrength: number; // 屈曲强度(kN)
  stabilityRatio: number; // 稳定系数
  isStable: boolean; // 是否稳定
  safetyMargin: number; // 安全余量
}

const BrbStabilityChecker: React.FC = () => {
  // 从localStorage加载初始状态
  const loadInitialState = () => {
    try {
      const savedParams = localStorage.getItem('brbStabilityParams');
      const initialParams = savedParams ? 
        JSON.parse(savedParams) as BrbStabilityParams :
        {
          id: '1',
          designForce: '',
          coreWidth: '',
          coreThickness: '',
          yieldStrength: '235',
          length: '',
          tubeWidth: '',
          tubeThickness: '',
          concreteStrength: '30'
        };
      
      return { params: initialParams };
    } catch (error) {
      console.error('加载初始状态失败:', error);
      // 加载失败时返回默认状态
      return {
        params: {
          id: '1',
          designForce: '',
          coreWidth: '',
          coreThickness: '',
          yieldStrength: '235',
          length: '',
          tubeWidth: '',
          tubeThickness: '',
          concreteStrength: '30'
        }
      };
    }
  };
  
  const initialState = loadInitialState();
  
  const [params, setParams] = useState<BrbStabilityParams>(initialState.params);
  const [results, setResults] = useState<StabilityResult | null>(null);
  const { showToast } = useToast();
  const [isCalculating, setIsCalculating] = useState(false);

  // 监听状态变化并保存到localStorage
  useEffect(() => {
    localStorage.setItem('brbStabilityParams', JSON.stringify(params));
  }, [params]);

  // 更新参数
  const updateParam = (field: keyof BrbStabilityParams, value: string) => {
    setParams(prev => ({ ...prev, [field]: value }));
  };

  // 计算BRB稳定性
  const calculateStability = () => {
    // 验证输入
    const requiredFields = ['designForce', 'coreWidth', 'coreThickness', 'yieldStrength', 'length', 'tubeWidth', 'tubeThickness', 'concreteStrength'];
    const missingFields = requiredFields.filter(field => !params[field]);
    
    if (missingFields.length > 0) {
      showToast(`请填写所有必填参数`, 'error');
      return;
    }

    setIsCalculating(true);

    try {
      // 转换为数值
      const N = parseFloat(params.designForce); // 设计力(kN)
      const b = parseFloat(params.coreWidth); // 芯板宽度(mm)
      const t = parseFloat(params.coreThickness); // 芯板厚度(mm)
      const f_y = parseFloat(params.yieldStrength); // 屈服强度(MPa)
      const L = parseFloat(params.length); // 支撑长度(mm)
      const B = parseFloat(params.tubeWidth); // 外套管宽度(mm)
      const T = parseFloat(params.tubeThickness); // 外套管厚度(mm)
      const f_c = parseFloat(params.concreteStrength); // 填充混凝土强度(MPa)

      // 计算芯板截面面积(mm²)
      const A = b * t;

      // 计算芯板屈服力(kN)
      const N_y = (A * f_y) / 1000;

      // 计算惯性矩(mm⁴)
      const I = (b * Math.pow(t, 3)) / 12;

      // 计算截面模量(mm³)
      const W = (b * Math.pow(t, 2)) / 6;

      // 计算回转半径(mm)
      const i = Math.sqrt(I / A);

      // 计算长细比
      const λ = L / i;

      // 计算屈曲强度(简化计算，实际工程中需要更复杂的公式)
      // 考虑外套管和混凝土的约束作用
      const k = 0.85; // 约束系数
      const E = 206000; // 弹性模量(MPa)
      const π = Math.PI;

      // 欧拉临界力
      const N_cr = (k * π² * E * I) / (Math.pow(L, 2)) / 1000; // kN

      // 考虑屈服强度和欧拉临界力的屈曲强度
      const N_b = Math.min(N_y, N_cr);

      // 稳定系数
      const γ = N / N_b;

      // 安全余量(%)
      const safetyMargin = ((N_b / N) - 1) * 100;

      // 判断是否稳定
      const isStable = γ <= 1.0;

      // 创建结果对象
      const result: StabilityResult = {
        id: params.id,
        slendernessRatio: parseFloat(λ.toFixed(2)),
        bucklingStrength: parseFloat(N_b.toFixed(2)),
        stabilityRatio: parseFloat(γ.toFixed(3)),
        isStable,
        safetyMargin: parseFloat(safetyMargin.toFixed(2))
      };

      setResults(result);
      showToast('稳定性核算完成', 'success');
    } catch (error) {
      console.error('计算失败:', error);
      showToast('计算失败，请检查输入参数', 'error');
    } finally {
      setIsCalculating(false);
    }
  };

  // 导出结果
  const exportResults = () => {
    if (!results) {
      showToast('没有可导出的结果', 'warning');
      return;
    }

    const data = {
      '设计力(kN)': params.designForce,
      '芯板宽度(mm)': params.coreWidth,
      '芯板厚度(mm)': params.coreThickness,
      '屈服强度(MPa)': params.yieldStrength,
      '支撑长度(mm)': params.length,
      '外套管宽度(mm)': params.tubeWidth,
      '外套管厚度(mm)': params.tubeThickness,
      '填充混凝土强度(MPa)': params.concreteStrength,
      '长细比': results.slendernessRatio,
      '屈曲强度(kN)': results.bucklingStrength,
      '稳定系数': results.stabilityRatio,
      '是否稳定': results.isStable ? '是' : '否',
      '安全余量(%)': results.safetyMargin
    };

    // 创建CSV内容
    const csvContent = '参数,数值\n' + 
      Object.entries(data).map(([key, value]) => `${key},${value}`).join('\n');

    // 创建Blob并下载
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `BRB稳定性核算结果_${new Date().toISOString().slice(0, 10)}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    showToast('结果导出成功', 'success');
  };

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* 页面标题 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            <Shield className="inline-block mr-3" />
            BRB稳定性核算
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            用于计算屈曲约束支撑(BRB)的稳定性参数
          </p>
        </div>

        {/* 左右布局容器 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          {/* 左边：参数输入区域 */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">输入参数</h2>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">设计力 (kN)</label>
                  <input
                    type="number"
                    value={params.designForce}
                    onChange={(e) => updateParam('designForce', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="输入设计力"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">芯板宽度 (mm)</label>
                  <input
                    type="number"
                    value={params.coreWidth}
                    onChange={(e) => updateParam('coreWidth', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="输入芯板宽度"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">芯板厚度 (mm)</label>
                  <input
                    type="number"
                    value={params.coreThickness}
                    onChange={(e) => updateParam('coreThickness', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="输入芯板厚度"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">屈服强度 (MPa)</label>
                  <input
                    type="number"
                    value={params.yieldStrength}
                    onChange={(e) => updateParam('yieldStrength', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="输入屈服强度"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">支撑长度 (mm)</label>
                  <input
                    type="number"
                    value={params.length}
                    onChange={(e) => updateParam('length', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="输入支撑长度"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">外套管宽度 (mm)</label>
                  <input
                    type="number"
                    value={params.tubeWidth}
                    onChange={(e) => updateParam('tubeWidth', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="输入外套管宽度"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">外套管厚度 (mm)</label>
                  <input
                    type="number"
                    value={params.tubeThickness}
                    onChange={(e) => updateParam('tubeThickness', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="输入外套管厚度"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">填充混凝土强度 (MPa)</label>
                  <input
                    type="number"
                    value={params.concreteStrength}
                    onChange={(e) => updateParam('concreteStrength', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="输入混凝土强度"
                  />
                </div>
              </div>

              <div className="flex justify-center mt-6">
                <button
                  onClick={calculateStability}
                  disabled={isCalculating}
                  className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-md shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-300 flex items-center"
                >
                  {isCalculating ? (
                    <span className="mr-2">核算中...</span>
                  ) : (
                    <>
                      <CheckCircle className="mr-2" />
                      开始核算
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* 右边：结果显示区域 */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-800">核算结果</h2>
              {results && (
                <button
                  onClick={exportResults}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md flex items-center text-sm"
                >
                  <Download className="mr-1 h-4 w-4" />
                  导出结果
                </button>
              )}
            </div>

            {results ? (
              <div className="space-y-6">
                <div className="bg-gray-50 p-4 rounded-md">
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">稳定性结论</h3>
                    </div>
                    <div className={`flex items-center px-4 py-2 rounded-full font-semibold ${results.isStable ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {results.isStable ? (
                        <>
                          <CheckCircle className="mr-2 h-5 w-5" />
                          稳定
                        </>
                      ) : (
                        <>
                          <AlertTriangle className="mr-2 h-5 w-5" />
                          不稳定
                        </>
                      )}
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 border border-gray-200 rounded-md">
                    <div className="text-sm text-gray-500 mb-1">长细比 (λ)</div>
                    <div className="text-2xl font-semibold text-gray-900">{results.slendernessRatio}</div>
                  </div>
                  <div className="p-4 border border-gray-200 rounded-md">
                    <div className="text-sm text-gray-500 mb-1">屈曲强度 (kN)</div>
                    <div className="text-2xl font-semibold text-gray-900">{results.bucklingStrength}</div>
                  </div>
                  <div className="p-4 border border-gray-200 rounded-md">
                    <div className="text-sm text-gray-500 mb-1">稳定系数 (γ)</div>
                    <div className="text-2xl font-semibold text-gray-900">{results.stabilityRatio}</div>
                  </div>
                  <div className="p-4 border border-gray-200 rounded-md">
                    <div className="text-sm text-gray-500 mb-1">安全余量 (%)</div>
                    <div className={`text-2xl font-semibold ${results.safetyMargin >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {results.safetyMargin}
                    </div>
                  </div>
                </div>

                <div className="bg-blue-50 p-4 rounded-md">
                  <h3 className="text-sm font-medium text-blue-900 mb-2">计算说明</h3>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• 稳定系数 γ = 设计力 / 屈曲强度</li>
                    <li>• γ ≤ 1.0 时，支撑稳定</li>
                    <li>• γ > 1.0 时，支撑不稳定</li>
                    <li>• 安全余量 = (屈曲强度 / 设计力 - 1) × 100%</li>
                  </ul>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-12 bg-gray-50 rounded-md">
                <Shield className="h-12 w-12 text-gray-400 mb-4" />
                <p className="text-gray-600 text-center">
                  请输入参数并点击"开始核算"按钮
                </p>
                <p className="text-sm text-gray-500 mt-2 text-center">
                  系统将自动计算BRB的稳定性参数
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BrbStabilityChecker;
