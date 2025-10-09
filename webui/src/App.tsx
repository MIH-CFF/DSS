import React from 'react';
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import { ConfigProvider } from 'antd';
import enUS from 'antd/locale/en_US';

import { CustomLayout } from './layout/CustomLayout';
import { LazyLanding } from './component/landing/LazyLanding';
import { LazyPage2 } from './component/LazyPage2';
import { LazyPage3 } from './component/LazyPage3';
import { DSAAnalysis } from './component/DSAAnalysis';

const App = () => (
  <ConfigProvider locale={enUS}>
    <BrowserRouter basename="/react-pipeline">
      <CustomLayout>
        <Routes>
          <Route path="/landing" element={<LazyLanding />} />
          <Route path="/analysis" element={<DSAAnalysis />} />
          <Route path="/page2" element={<LazyPage2 />} />
          <Route path="/page3" element={<LazyPage3 />} />
          <Route
            path="*"
            element={<Navigate to="/analysis" replace />}
          />
        </Routes>
      </CustomLayout>
    </BrowserRouter>
  </ConfigProvider>
);

// eslint-disable-next-line import/no-default-export
export default App;
