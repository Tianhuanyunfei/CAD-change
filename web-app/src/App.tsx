import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import BrbDesigner from './pages/BrbDesigner';
import BrbDrawing from './pages/BrbDrawing';
import VfdDesigner from './pages/VfdDesigner';
import DxfToCsvConverter from './pages/DxfToCsvConverter';
import CsvToDxfConverter from './pages/CsvToDxfConverter';
import CsvEditor from './pages/CsvEditor';
import Settings from './pages/Settings';
import './index.css';

function App() {
  // 在应用加载时应用保存的背景色
  useEffect(() => {
    const savedColor = localStorage.getItem('backgroundColor');
    if (savedColor) {
      // 应用到body元素
      document.body.style.backgroundColor = savedColor;
      
      // 应用到所有带有min-h-screen类的div元素（包括Layout和Dashboard组件中的）
      const minHeightDivs = document.querySelectorAll('.min-h-screen');
      minHeightDivs.forEach(div => {
        div.classList.remove('bg-gray-50');
        div.style.backgroundColor = savedColor;
      });
      
      // 应用到main元素
      const mainElement = document.querySelector('main');
      if (mainElement) {
        mainElement.style.backgroundColor = savedColor;
      }
      
      // 应用到main内的div容器
      const mainDiv = document.querySelector('main > div');
      if (mainDiv) {
        mainDiv.style.backgroundColor = savedColor;
      }
      
      // 应用到所有卡片元素
      const cards = document.querySelectorAll('.card');
      cards.forEach(card => {
        card.classList.remove('bg-white');
        card.style.backgroundColor = '#ffffff'; // 保持卡片为白色，以便与背景形成对比
      });
      
      // 应用到Dashboard组件中的内容容器
      const dashboardContainers = document.querySelectorAll('.max-w-7xl.mx-auto');
      dashboardContainers.forEach(container => {
        container.style.backgroundColor = savedColor;
      });
    }
  }, []);

  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/brb-designer" element={<BrbDesigner />} />
          <Route path="/brb-drawing" element={<BrbDrawing />} />
          <Route path="/vfd-designer" element={<VfdDesigner />} />
          <Route path="/dxf-to-csv" element={<DxfToCsvConverter />} />
          <Route path="/csv-to-dxf" element={<CsvToDxfConverter />} />
          <Route path="/csv-editor" element={<CsvEditor />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;