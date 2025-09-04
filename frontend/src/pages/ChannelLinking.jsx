import ChannelIcon from "../assets/channel-linking.png";
import WhatsappIcon from "../assets/whatsapp.png";
import TelegramIcon from "../assets/telegram.png";

const ChannelLinking = () => {
  return (
    <div className="mt-4">
      <div className="flex items-center mb-2">
        <div className="text-xl mr-2">Channel Linking</div>
        <img src={ChannelIcon} alt="" className="w-5 h-5" />
        <div className="ml-auto border border-black px-2 py-1 rounded-md hover:bg-red-500 cursor-pointer">
          Configuration
        </div>
      </div>
      <div className="border border-black px-4 py-2 rounded-lg h-32">
        <div>
          {/* <p>Select channels to link:</p>
              <hr className="border-t border-gray-300 mt-2"></hr> */}
        </div>

        <div className="flex items-center">
          {/* Add your channel linking options here */}
          <div className="mr-8">
            <img src={WhatsappIcon} className="w-16" alt="" />
            WhatsApp
            <div className="flex justify-center border border-black rounded-sm">
              Link
            </div>
          </div>
          <div>
            <img src={TelegramIcon} className="w-16" alt="" />
            Telegram
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChannelLinking;
