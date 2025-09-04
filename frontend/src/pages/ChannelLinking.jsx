import ChannelIcon from "../assets/channel-linking.png";
import WhatsappIcon from "../assets/whatsapp.png";
import TelegramIcon from "../assets/telegram.png";
import Configuration from "../components/Configuration";
import React, { useState } from "react";

const ChannelLinking = () => {

  return (
    <div className="mt-4">
      <div className="flex items-center mb-2">
        <div className="text-xl mr-2">Channel Linking</div>
        <img src={ChannelIcon} alt="" className="w-5 h-5" />
        <div className="ml-auto">
          <Configuration />
        </div>
      </div>

      <div className="border border-black px-4 py-2 rounded-lg">
        <div>
          {/* <p>Select channels to link:</p>
              <hr className="border-t border-gray-300 mt-2"></hr> */}
        </div>

        <div className="flex items-center">
          {/* Add your channel linking options here */}
          <div className="mr-8">
            <div className="flex flex-col items-center justify-center">
              <img src={WhatsappIcon} className="w-16 mb-1" alt="" />
              WhatsApp
              <div className="flex justify-center border border-black rounded-sm px-6 cursor-pointer mt-1">
                Link
              </div>
            </div>
          </div>
          <div className="flex flex-col items-center justify-center">
            <img src={TelegramIcon} className="w-16 mb-1" alt="" />
            Telegram
            <div className="flex justify-center border border-black rounded-sm px-6 cursor-pointer mt-1">
              Link
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChannelLinking;
