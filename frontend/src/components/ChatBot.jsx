import { useState } from "react";
import { MessageCircle } from "lucide-react"; // nice icon from lucide-react

const ChatBot = () => {
  const [open, setOpen] = useState(false);

  return (
    <div>
      {/* Floating button */}
      <div
        className="fixed bottom-6 right-6 bg-blue-600 text-white p-4 rounded-full shadow-lg cursor-pointer hover:bg-blue-700 transition"
        onClick={() => setOpen(!open)}
      >
        <MessageCircle size={28} />
      </div>

      {/* Chat window */}
      {open && (
        <div className="fixed bottom-20 right-6 w-80 h-96 bg-white shadow-xl rounded-2xl flex flex-col overflow-hidden">
          {/* Header */}
          <div className="bg-blue-600 text-white p-3 font-semibold flex justify-between items-center">
            AI Chatbot
            <button onClick={() => setOpen(false)}>✕</button>
          </div>

          {/* Chat body */}
          <div className="flex-1 p-3 overflow-y-auto text-sm">
            {/* Example messages */}
            <div className="mb-2">
              <div className="bg-gray-200 p-2 rounded-lg inline-block">
                Hello! 👋 How can I help you today?
              </div>
            </div>
          </div>

          {/* Input */}
          <div className="p-2 border-t flex">
            <input
              type="text"
              placeholder="Type a message..."
              className="flex-1 border rounded-lg px-2 py-1 text-sm"
            />
            <button className="ml-2 bg-blue-600 text-white px-3 py-1 rounded-lg hover:bg-blue-700">
              Send
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatBot;
