import ChannelIcon from "../assets/channel-linking.png";
import TelegramIcon from "../assets/telegram.png";
import GoogleCalendarIcon from "../assets/google-calendar.png";
import React, { useState, useEffect } from "react";
import Toast from "../components/Toast";
import useSuccessNotification from "../hooks/useSuccessNotification";

const ChannelLinking = () => {
  const [telegramBotId, setTelegramBotId] = useState("");
  const [clientSecretJsonContent, setClientSecretJsonContent] = useState("");
  const [toneAndManner, setToneAndManner] = useState("");
  const [message, setMessage] = useState("");
  const [agentMessage, setAgentMessage] = useState("");
  const [currentTone, setCurrentTone] = useState("");
  const [googleCalendarStatus, setGoogleCalendarStatus] = useState({ configured: false, ready: false, token_exists: false });
  const [authorizationCode, setAuthorizationCode] = useState("");
  const [showAuthCodeInput, setShowAuthCodeInput] = useState(false);
  
  // Toast notification state and hook
  const [toast, setToast] = useState({ show: false, type: '', title: '', message: '' });
  const { showSuccess, showError } = useSuccessNotification(setToast);

  useEffect(() => {
    (async () => {
      try {
        const resp = await fetch('http://localhost:8000/config/current');
        if (resp.ok) {
          const data = await resp.json();
          setCurrentTone(data.tone_and_manner || "");
        }
      } catch (e) { /* ignore */ }
      
      // Check Google Calendar status
      try {
        const resp = await fetch('http://localhost:8000/google/calendar/status');
        if (resp.ok) {
          const data = await resp.json();
          setGoogleCalendarStatus(data);
        }
      } catch (e) { /* ignore */ }
    })();

    // Listen for OAuth completion messages from popup window
    const handleMessage = (event) => {
      if (event.origin !== window.location.origin) return;
      
      if (event.data.type === 'GOOGLE_OAUTH_SUCCESS') {
        showSuccess('Authorization Complete', 'Google Calendar has been successfully authorized!');
        checkGoogleCalendarStatus();
      } else if (event.data.type === 'GOOGLE_OAUTH_ERROR') {
        showError('Authorization Failed', event.data.message || 'Google Calendar authorization failed.');
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [showSuccess, showError]); // Added missing dependencies
  // Restart backend feature removed (hot-reload no longer required after config save)

  const handleChannelSubmit = async (e) => {
    e.preventDefault();
    setMessage(""); // Clear previous messages

    if (!telegramBotId) {
      setMessage("Please enter Telegram Bot ID.");
      showError('Missing Information', 'Please enter Telegram Bot ID.');
      return;
    }

    // Validate JSON content if provided
    if (clientSecretJsonContent) {
      try {
        JSON.parse(clientSecretJsonContent);
      } catch (error) {
        const errorMsg = "Invalid JSON for Google Calendar Client Secret.";
        setMessage(errorMsg);
        showError('Invalid JSON', errorMsg);
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
        const successMsg = data.message || "Channel configuration saved.";
        setMessage(successMsg);
        setTelegramBotId("");
        setClientSecretJsonContent("");
        showSuccess('Configuration Saved', 'Channel configuration has been successfully saved.');
        
        // Automatically trigger Google OAuth if auth URL is provided
        if (data.google_auth_url) {
          setTimeout(() => {
            window.open(data.google_auth_url, '_blank', 'width=500,height=600');
            showSuccess('Authorization Started', 'Please complete Google Calendar authorization in the new window and copy the authorization code when shown.');
            setShowAuthCodeInput(true);
          }, 1000); // Small delay to show the success message first
        }
        
        // After successful channel config, check Google Calendar status
        checkGoogleCalendarStatus();
      } else {
        let errorMsg = "Failed to save configuration.";
        if (data.detail) {
          if (typeof data.detail === 'string') {
            errorMsg = data.detail;
          } else if (Array.isArray(data.detail)) {
            // Handle Pydantic validation errors
            errorMsg = data.detail.map(err => err.msg || 'Validation error').join(', ');
          } else {
            errorMsg = JSON.stringify(data.detail);
          }
        }
        setMessage(errorMsg);
        showError('Configuration Failed', errorMsg);
      }
    } catch (error) {
      console.error("Error configuring Telegram channel:", error);
      const errorMsg = "An error occurred during configuration.";
      setMessage(errorMsg);
      showError('Configuration Error', errorMsg);
    }
  };

  const checkGoogleCalendarStatus = async () => {
    try {
      const resp = await fetch('http://localhost:8000/google/calendar/status');
      if (resp.ok) {
        const data = await resp.json();
        setGoogleCalendarStatus(data);
      }
    } catch (e) { /* ignore */ }
  };

  const handleGoogleAuthorization = async () => {
    try {
      const resp = await fetch('http://localhost:8000/google/oauth/start');
      if (resp.ok) {
        const data = await resp.json();
        // Open authorization URL in new window
        window.open(data.auth_url, '_blank', 'width=500,height=600');
        showSuccess('Authorization Started', 'Please complete authorization in the new window and copy the authorization code.');
        setShowAuthCodeInput(true);
      } else {
        showError('Authorization Failed', 'Failed to start Google authorization.');
      }
    } catch (error) {
      showError('Authorization Error', 'Error starting Google authorization.');
    }
  };

  const handleAuthCodeSubmit = async () => {
    if (!authorizationCode.trim()) {
      showError('Missing Code', 'Please enter the authorization code.');
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/google/oauth/callback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          authorization_code: authorizationCode.trim()
        })
      });

      const data = await response.json();

      if (response.ok) {
        showSuccess('Authorization Complete', 'Google Calendar has been successfully authorized!');
        setAuthorizationCode("");
        setShowAuthCodeInput(false);
        checkGoogleCalendarStatus();
      } else {
        showError('Authorization Failed', data.detail || 'Failed to complete authorization.');
      }
    } catch (error) {
      showError('Authorization Error', 'Error completing authorization.');
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
        const successMsg = data.message || 'Agent configuration updated.';
        setAgentMessage(successMsg);
        if (data.tone_and_manner) {
          setCurrentTone(data.tone_and_manner);
          setToneAndManner("");
        }
        showSuccess('Agent Updated', 'Agent tone and manner configuration has been successfully updated.');
      } else {
        let errorMsg = 'Failed to update agent configuration.';
        if (data.detail) {
          if (typeof data.detail === 'string') {
            errorMsg = data.detail;
          } else if (Array.isArray(data.detail)) {
            // Handle Pydantic validation errors
            errorMsg = data.detail.map(err => err.msg || 'Validation error').join(', ');
          } else {
            errorMsg = JSON.stringify(data.detail);
          }
        }
        setAgentMessage(errorMsg);
        showError('Update Failed', errorMsg);
      }
    } catch (err) {
      const errorMsg = 'Error updating agent configuration.';
      setAgentMessage(errorMsg);
      showError('Configuration Error', errorMsg);
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
                
                {/* Google Calendar Status */}
                <div className="mt-2 text-responsive-xs">
                  <div className={`flex items-center space-x-2 ${googleCalendarStatus.ready ? 'text-green-600' : 'text-orange-600'}`}>
                    <span className={`w-2 h-2 rounded-full ${googleCalendarStatus.ready ? 'bg-green-500' : 'bg-orange-500'}`}></span>
                    <span>
                      {googleCalendarStatus.ready 
                        ? "✅ Google Calendar Ready" 
                        : googleCalendarStatus.configured 
                          ? "⚠️ Needs Authorization" 
                          : "❌ Client Secret Required"
                      }
                    </span>
                  </div>
                  {googleCalendarStatus.configured && !googleCalendarStatus.ready && (
                    <div className="mt-2 space-y-2">
                      <button
                        type="button"
                        onClick={handleGoogleAuthorization}
                        className="px-3 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                      >
                        Authorize Google Calendar
                      </button>
                      
                      {showAuthCodeInput && (
                        <div className="space-y-2">
                          <input
                            type="text"
                            placeholder="Paste authorization code here..."
                            value={authorizationCode}
                            onChange={(e) => setAuthorizationCode(e.target.value)}
                            className="w-full px-2 py-1 text-xs border border-gray-300 rounded"
                          />
                          <button
                            type="button"
                            onClick={handleAuthCodeSubmit}
                            className="px-3 py-1 text-xs bg-green-500 text-white rounded hover:bg-green-600 transition-colors"
                          >
                            Submit Code
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                </div>
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
      {toast.show && (
        <Toast
          type={toast.type}
          title={toast.title}
          message={toast.message}
          onClose={() => setToast({ ...toast, show: false })}
        />
      )}
    </div>
  );
};

export default ChannelLinking;
