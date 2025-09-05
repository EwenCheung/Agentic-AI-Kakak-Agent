import React from "react";
import Header from "../components/Header";
import DashBoardIcon from "../assets/dashboard.png";
import ChannelLinking from "./ChannelLinking";
import ChatBot from "../components/ChatBot";

const DashboardPage = () => {
  return (
    <div>
      <div className="rounded-lg py-4">
        <div className="flex items-center mb-2">
          <h1 className="text-xl mr-2">Dashboard</h1>
          <img src={DashBoardIcon} className="w-5 h-5" alt="Dashboard Icon" />
        </div>

        <div className="border border-black px-4 py-2 rounded-lg">
          <p>Daily Digest</p>
          <hr class="border-t border-gray-500 mt-2"></hr>
          <div className="grid grid-cols-1 grid-rows-3 gap-4">
            <div>
              <div className="mt-2">Upcoming Events</div>
              {/* fetch from backend */}
            </div>
            <div>
              <div className="mt-4">Tickets</div>
              {/* fetch from backend */}
            </div>

            <div>
              <div className="mt-4">Insights</div>
              {/* fetch from backend */}
            </div>
          </div>
        </div>
      </div>
      <ChannelLinking/>
      <ChatBot/>
    </div>
  );
};

export default DashboardPage;
