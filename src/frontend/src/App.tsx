import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from '@components/Layout';
import Dashboard from '@pages/Dashboard';
import ImageManager from '@pages/ImageManager';
import Components from '@pages/Components';
import Registry from '@pages/Registry';
import Deployment from '@pages/Deployment';
import Workflows from '@pages/Workflows';
import Settings from '@pages/Settings';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/images" element={<ImageManager />} />
          <Route path="/components" element={<Components />} />
          <Route path="/registry" element={<Registry />} />
          <Route path="/deployment" element={<Deployment />} />
          <Route path="/workflows" element={<Workflows />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
