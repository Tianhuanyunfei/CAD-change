import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Box, 
  Zap, 
  FileText, 
  FileSpreadsheet, 
  Table,
  Settings,
  ChevronDown, 
  ChevronRight
} from 'lucide-react';

const Dashboard: React.FC = () => {
  // 为每个分类添加折叠状态管理，默认都展开
  const [collapsedCategories, setCollapsedCategories] = React.useState<{ [key: number]: boolean }>({});
  
  // 切换分类的折叠状态
  const toggleCategory = (categoryId: number) => {
    setCollapsedCategories(prev => ({
      ...prev,
      [categoryId]: !prev[categoryId]
    }));
  };
  
  const categories = [
    {
      id: 1,
      name: '图纸设计',
      functions: [
        {
          id: 3,
          title: 'BRB图纸设计',
          description: 'BRB图纸参数化设计',
          icon: Box,
          color: 'bg-orange-500',
          link: '/brb-drawing'
        }
      ]
    },
    {
      id: 2,
      name: '文件转换',
      functions: [
        {
          id: 3,
          title: 'DXF转CSV',
          description: '将DXF文件转换为CSV格式',
          icon: FileText,
          color: 'bg-purple-500',
          link: '/dxf-to-csv'
        },
        {
          id: 4,
          title: 'CSV转DXF',
          description: '将CSV文件转换为DXF格式',
          icon: FileSpreadsheet,
          color: 'bg-indigo-500',
          link: '/csv-to-dxf'
        }
      ]
    },
    {
      id: 3,
      name: '数据处理',
      functions: [
        {
          id: 5,
          title: 'CSV编辑器',
          description: '在线编辑CSV文件数据',
          icon: Table,
          color: 'bg-blue-500',
          link: '/csv-editor'
        }
      ]
    },
    {
      id: 5,
      name: '开发中',
      functions: [
        {
          id: 1,
          title: 'BRB产品设计',
          description: '屈曲约束支撑参数化设计，包含屈服力及稳定性的核算',
          icon: Box,
          color: 'bg-orange-500',
          link: '/brb-designer'
        },
        {
          id: 2,
          title: '粘滞产品设计',
          description: '粘滞阻尼器参数化设计',
          icon: Zap,
          color: 'bg-green-500',
          link: '/vfd-designer'
        }
      ]
    },
    {
      id: 4,
      name: '系统设置',
      functions: [
        {
          id: 6,
          title: '系统设置',
          description: '配置系统参数和偏好设置',
          icon: Settings,
          color: 'bg-purple-500',
          link: '/settings'
        }
      ]
    }
  ];

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      {/* 页面标题 */}
      <div className="max-w-7xl mx-auto mb-12">
        <h1 className="text-3xl font-bold text-gray-900">设计工具集</h1>
        <p className="mt-2 text-lg text-gray-600">专业的CAD参数化设计与文件转换平台</p>
      </div>

      {/* 分类功能区域 */}
      <div className="max-w-7xl mx-auto space-y-12">
        {categories.map((category) => (
          <div key={category.id} className="space-y-6">
            {/* 分类标题 */}
            <div className="flex items-center space-x-3">
              <div className="text-xl font-bold text-gray-900">{category.name}</div>
              <button 
                className="flex items-center justify-center w-10 h-10 bg-brb-blue-100 hover:bg-brb-blue-200 text-brb-blue-600 hover:text-brb-blue-800 transition-all duration-300 rounded-full"
                onClick={() => toggleCategory(category.id)}
              >
                {collapsedCategories[category.id] ? <ChevronRight className="h-6 w-6 font-bold" /> : <ChevronDown className="h-6 w-6 font-bold" />}
              </button>
            </div>

            {/* 功能方块 */}
            <div 
              className={`grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 overflow-hidden transition-all duration-300 ease-in-out ${collapsedCategories[category.id] ? 'max-h-0 opacity-0' : 'max-h-96 opacity-100'}`}
            >
              {category.functions.map((func) => (
                <Link
                  key={func.id}
                  to={func.link}
                  className="group relative overflow-hidden bg-white border border-gray-200 rounded-xl hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-50 to-purple-50 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  <div className="relative p-6">
                    <div className="flex flex-col items-center text-center">
                      <div className={`p-4 rounded-xl ${func.color} text-white shadow-lg group-hover:scale-110 transition-transform duration-300 mb-4`}>
                        <func.icon className="h-8 w-8" />
                      </div>
                      <h3 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors duration-300 mb-2">
                        {func.title}
                      </h3>
                      <p className="text-sm text-gray-500">{func.description}</p>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;