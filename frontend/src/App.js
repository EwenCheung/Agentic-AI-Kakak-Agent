import React from 'react';
import DashboardPage from './pages/DashboardPage';
import './App.css';
// import "@fontsource/montserrat"; 
// import "@fontsource/montserrat/400.css"; 
// import "@fontsource/montserrat/400-italic.css"; 
import Header from './components/Header';
import ChannelLinking from './pages/ChannelLinking';

function App() {
  return (
    <div className="mx-auto max-w-7xl my-8 mx-4">
      <Header/>
      <DashboardPage/>
      <ChannelLinking/>
    </div>
  );
}

export default App;
