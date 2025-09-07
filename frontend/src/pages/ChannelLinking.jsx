import ChannelIcon from "../assets/channel-linking.png";
import TelegramIcon from "../assets/telegram.png";
import GoogleCalendarIcon from "../assets/google-calendar.png";
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
    <div className="spacing-responsive">
      <div className="flex items-center mb-4">
        <div className="text-responsive-xl mr-2">Configuration</div>
        <img src={ChannelIcon} alt="" className="w-5 h-5 md:w-6 md:h-6" />
      </div>

      <div className="border border-black px-2 py-4 md:px-4 md:py-8 lg:px-6 lg:py-10 rounded-lg">
        <div className="flex flex-col items-center justify-center space-y-6">
          {/* Telegram Section */}
          <div className="w-full max-w-md">
            <div className="flex flex-col items-center mb-4">
              <img src={TelegramIcon} className="w-12 h-12 md:w-16 md:h-16 mb-2" alt="Telegram" />
              <h3 className="text-responsive-base font-semibold">Telegram</h3>
            </div>
            
            <form onSubmit={handleChannelSubmit} className="space-y-4">
              <div>
                <label htmlFor="telegramBotId" className="block text-responsive-sm font-medium text-gray-700 mb-1">
                  Telegram Bot ID:
                </label>
                <input
                  type="text"
                  id="telegramBotId"
                  className="w-full rounded-md border-gray-300 shadow-sm 
                    focus:border-indigo-300 focus:ring focus:ring-indigo-200 
                    focus:ring-opacity-50 text-responsive-sm px-3 py-2"
                  value={telegramBotId}
                  onChange={(e) => setTelegramBotId(e.target.value)}
                  required
                />
              </div>
              
              <div>
                <label htmlFor="clientSecretJsonContent" className="flex items-center mb-1 text-responsive-sm font-medium text-gray-700">
                  <img src={GoogleCalendarIcon} alt="" className="h-4 w-4 mr-1" /> 
                  Google Calendar Client Secret (JSON):
                </label>
                <textarea
                  id="clientSecretJsonContent"
                  rows="6"
                  className="w-full rounded-md border-gray-300 shadow-sm 
                    focus:border-indigo-300 focus:ring focus:ring-indigo-200 
                    focus:ring-opacity-50 font-mono text-responsive-xs px-3 py-2"
                  value={clientSecretJsonContent}
                  onChange={(e) => setClientSecretJsonContent(e.target.value)}
                  placeholder="Paste your client_secret.json content here..."
                />
              </div>
              
              <button
                type="submit"
                className="w-full flex justify-center border border-black rounded-md 
                  px-6 py-2 bg-blue-500 text-white hover:bg-blue-600 
                  text-responsive-sm font-medium transition-colors duration-200"
              >
                Save Channel Config
              </button>
            </form>
            
            {message && (
              <p className="mt-3 text-responsive-sm p-3 rounded-md bg-gray-50 border border-gray-200">
                {message}
              </p>
            )}
          </div>

          {/* Agent Configuration Section */}
          <div className="w-full max-w-md border-t border-gray-300 pt-6">
            <div className="space-y-4">
              <div>
                <h4 className="font-semibold text-responsive-sm mb-1">Agent Configuration</h4>
                <div className="text-responsive-xs text-gray-600 mb-3">
                  Current tone: <span className="font-medium">{currentTone || '(default)'}</span>
                </div>
              </div>
              
              <form onSubmit={handleAgentSubmit} className="space-y-4">
                <div>
                  <label htmlFor="toneAndManner" className="block text-responsive-sm font-medium text-gray-700 mb-1">
                    Tone & Manner:
                  </label>
                  <select
                    id="toneAndManner"
                    className="w-full rounded-md border-gray-300 bg-white shadow-sm 
                      focus:border-indigo-300 focus:ring focus:ring-indigo-200 
                      focus:ring-opacity-50 text-responsive-sm px-3 py-2"
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
                </div>
                
                <button
                  type="submit"
                  className="w-full flex justify-center border border-black rounded-md 
                    px-6 py-2 bg-green-600 text-white hover:bg-green-700 
                    text-responsive-sm font-medium transition-colors duration-200"
                >
                  Save Agent Config
                </button>
              </form>
              
              {agentMessage && (
                <p className="text-responsive-sm p-3 rounded-md bg-gray-50 border border-gray-200">
                  {agentMessage}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChannelLinking;
