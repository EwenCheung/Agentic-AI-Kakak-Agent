import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import DashboardPage from "./pages/DashboardPage";
import ConfigurationPage from "./pages/ConfigurationPage";
import KnowledgeBaseUpload from "./pages/KnowledgeBaseUpload";
import GoogleOAuthCallback from "./pages/GoogleOAuthCallback";
// import TicketsPage from "./pages/TicketsPage.jsx";
import Header from "./components/Header";
import "./App.css";

function App() {
  return (
    <Router>
      <div className="responsive-container my-4 sm:my-6 md:my-8">
        <Header />
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/config" element={<ConfigurationPage />} />
          <Route path="/channel-linking" element={<ConfigurationPage />} />
          <Route path="/knowledge-base-upload" element={<KnowledgeBaseUpload />} />
          <Route path="/google/oauth/callback" element={<GoogleOAuthCallback />} />
          {/* <Route path="/tickets" element={<TicketsPage />} /> */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;
