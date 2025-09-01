import React from "react";
import Header from "../components/Header";
import DashBoardIcon from "../assets/dashboard.png";

const DashboardPage = () => {
  return (
    <div>
      <div className="rounded-lg py-4">
        <div className="flex items-center mb-2">
          <h1 className="text-xl mr-2">Dashboard</h1>
          <img src={DashBoardIcon} className="w-5 h-5" alt="Dashboard Icon" />
        </div>

        <div className="border border-black px-4 py-2 rounded-lg h-64">
          <p>Daily Digest</p>
          <hr class="border-t border-gray-300 mt-2"></hr>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
