import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import AssetInventory from './pages/AssetInventory'
import AssetDiscovery from './pages/AssetDiscovery'
import CBOM from './pages/CBOM'
import PosturePQC from './pages/PosturePQC'
import CyberRating from './pages/CyberRating'
import AICopilot from './pages/AICopilot'
import Reporting from './pages/Reporting'

export default function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/assets" element={<AssetInventory />} />
          <Route path="/discovery" element={<AssetDiscovery />} />
          <Route path="/cbom" element={<CBOM />} />
          <Route path="/posture" element={<PosturePQC />} />
          <Route path="/cyber-rating" element={<CyberRating />} />
          <Route path="/ai-copilot" element={<AICopilot />} />
          <Route path="/reporting" element={<Reporting />} />
        </Routes>
      </Layout>
    </Router>
  )
}
