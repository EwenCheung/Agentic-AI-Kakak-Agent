import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import DashboardPage from "./pages/DashboardPage";
import ChannelLinking from "./pages/ChannelLinking";
import TicketPage from "./pages/Ticket";
import Header from "./components/Header";
import "./App.css";

function App() {
  return (
    <Router>
      <div className="mx-auto max-w-7xl my-8 mx-4">
        <Header />
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/tickets" element={<TicketPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
