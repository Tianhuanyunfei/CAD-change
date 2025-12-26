import React from 'react';
import { Building2, User } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white shadow-brb-lg border-b border-gray-200">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-3">
            <Building2 className="h-8 w-8 text-brb-blue-600" />
            <div>
              <h1 className="text-xl font-bold text-gray-900">设计工具</h1>
              <p className="text-sm text-gray-600"> 阻尼器设计软件</p>
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <User className="h-4 w-4" />
            <span>工程师</span>
          </div>
          <div className="w-8 h-8 bg-brb-blue-600 rounded-full flex items-center justify-center">
            <span className="text-white text-sm font-semibold">工</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;