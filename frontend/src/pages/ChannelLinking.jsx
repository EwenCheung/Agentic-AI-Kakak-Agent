import ChannelIcon from "../assets/channel-linking.png";
import TelegramIcon from "../assets/telegram.png";
import Configuration from "../components/Configuration";
import React, { useState, useEffect } from "react";

const ChannelLinking = () => {
  const [telegramBotId, setTelegramBotId] = useState("");
  const [clientSecretJsonContent, setClientSecretJsonContent] = useState("");
  const [toneAndManner, setToneAndManner] = useState("");
  const [message, setMessage] = useState("");
  const [agentMessage, setAgentMessage] = useState("");
  const [currentTone, setCurrentTone] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const resp = await fetch('http://localhost:8000/config/current');
        if (resp.ok) {
          const data = await resp.json();
          setCurrentTone(data.tone_and_manner || "");
        }
      } catch (e) { /* ignore */ }
    })();
  }, []);
  // Restart backend feature removed (hot-reload no longer required after config save)

  const handleChannelSubmit = async (e) => {
    e.preventDefault();
    setMessage(""); // Clear previous messages

    if (!telegramBotId) {
      setMessage("Please enter Telegram Bot ID.");
      return;
    }

    // Validate JSON content if provided
    if (clientSecretJsonContent) {
      try {
        JSON.parse(clientSecretJsonContent);
      } catch (error) {
        setMessage("Invalid JSON for Google Calendar Client Secret.");
        return;
      }
    }

    const payload = {
      telegram_bot_id: telegramBotId,
      client_secret_json_content: clientSecretJsonContent,
    };

    try {
  const response = await fetch('http://localhost:8000/configure_channel', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json', // Changed header for JSON payload
        },
        body: JSON.stringify(payload), // Send as JSON
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(data.message || "Channel configuration saved.");
        setTelegramBotId("");
        setClientSecretJsonContent("");
      } else {
        setMessage(typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail) || "Failed to save configuration.");
      }
    } catch (error) {
      console.error("Error configuring Telegram channel:", error);
      setMessage("An error occurred during configuration.");
    }
  };

  const handleAgentSubmit = async (e) => {
    e.preventDefault();
    setAgentMessage("");
    const payload = { tone_and_manner: toneAndManner || null };
    try {
      const resp = await fetch('http://localhost:8000/configure_agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await resp.json();
      if (resp.ok) {
        setAgentMessage(data.message || 'Agent configuration updated.');
        if (data.tone_and_manner) {
          setCurrentTone(data.tone_and_manner);
          setToneAndManner("");
        }
      } else {
        setAgentMessage(data.detail || 'Failed to update agent configuration.');
      }
    } catch (err) {
      setAgentMessage('Error updating agent configuration.');
    }
  };

  return (
    <div className="mt-4">
      <div className="flex items-center mb-2">
        <div className="text-xl mr-2">Channel Configuration</div> {/* Changed title */}
        <img src={ChannelIcon} alt="" className="w-5 h-5" />
        <div className="ml-auto">
          <Configuration />
        </div>
      </div>

      <div className="border border-black px-4 py-2 rounded-lg">
        <div className="flex flex-col items-center justify-center"> {/* Centered content */}
          <img src={TelegramIcon} className="w-16 mb-1" alt="Telegram" />
          Telegram
          <form onSubmit={handleChannelSubmit} className="flex flex-col items-center mt-2 w-full">
            <div className="mb-2">
              <label htmlFor="telegramBotId" className="block text-sm font-medium text-gray-700">
                Telegram Bot ID:
              </label>
              <input
                type="text"
                id="telegramBotId"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                value={telegramBotId}
                onChange={(e) => setTelegramBotId(e.target.value)}
                required
              />
            </div>
            <div className="mb-2">
              <label htmlFor="clientSecretJsonContent" className="block text-sm font-medium text-gray-700">
                Google Calendar Client Secret (Paste JSON content):
              </label>
              <textarea
                id="clientSecretJsonContent"
                rows="8" // Increased rows for better visibility
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 font-mono text-xs" // Added font-mono and text-xs for JSON
                value={clientSecretJsonContent}
                onChange={(e) => setClientSecretJsonContent(e.target.value)}
                placeholder="Paste your client_secret.json content here..."
              ></textarea>
            </div>
            <button
              type="submit"
              className="flex justify-center border border-black rounded-sm px-6 py-1 cursor-pointer mt-1 bg-blue-500 text-white hover:bg-blue-600"
            >
              Save Channel Config
            </button>
          </form>
          {message && <p className="mt-2 text-sm">{message}</p>}
          <div className="w-full border-t border-gray-300 mt-4 pt-4">
            <div className="font-semibold text-sm mb-1">Agent Configuration</div>
            <div className="text-xs text-gray-600 mb-2">Current tone: {currentTone || '(default)'} </div>
            <form onSubmit={handleAgentSubmit} className="flex flex-col items-start w-full">
              <label htmlFor="toneAndManner" className="block text-sm font-medium text-gray-700">
                Tone & Manner:
              </label>
              <select
                id="toneAndManner"
                className="mt-1 mb-2 block w-full rounded-md border-gray-300 bg-white shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                value={toneAndManner}
                onChange={(e) => setToneAndManner(e.target.value)}
              >
                <option value="">(Keep current)</option>
                <option value="Friendly and Professional">Friendly & Professional</option>
                <option value="Formal and Respectful">Formal & Respectful</option>
                <option value="Casual and Approachable">Casual & Approachable</option>
                <option value="Empathetic and Supportive">Empathetic & Supportive</option>
                <option value="Concise and Direct">Concise & Direct</option>
                <option value="Enthusiastic and Positive">Enthusiastic & Positive</option>
              </select>
              <button
                type="submit"
                className="flex justify-center border border-black rounded-sm px-6 py-1 cursor-pointer bg-green-600 text-white hover:bg-green-700"
              >
                Save Agent Config
              </button>
            </form>
            {agentMessage && <p className="mt-2 text-sm">{agentMessage}</p>}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChannelLinking;
