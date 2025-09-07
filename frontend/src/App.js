import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import DashboardPage from "./pages/DashboardPage";
import ConfigurationPage from "./pages/ConfigurationPage";
import KnowledgeBaseUpload from "./pages/KnowledgeBaseUpload";
// import TicketsPage from "./pages/TicketsPage.jsx";
import Header from "./components/Header";
import "./App.css";

function App() {
  return (
    <Router>
      <div className="mx-auto max-w-7xl my-8 mx-4">
        <Header />
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/config" element={<ConfigurationPage />} />
          <Route path="/knowledge-base-upload" element={<KnowledgeBaseUpload />} />
          {/* <Route path="/tickets" element={<TicketsPage />} /> */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;
