import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const GoogleOAuthCallback = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [status, setStatus] = useState('processing');
  const [message, setMessage] = useState('Processing Google authorization...');

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Extract authorization code from URL
        const urlParams = new URLSearchParams(location.search);
        const code = urlParams.get('code');
        const state = urlParams.get('state');
        const error = urlParams.get('error');

        if (error) {
          setStatus('error');
          setMessage(`Authorization failed: ${error}`);
          
          // Send error to parent window if popup
          if (window.opener) {
            window.opener.postMessage({
              type: 'GOOGLE_OAUTH_ERROR',
              message: `Authorization failed: ${error}`
            }, window.location.origin);
          }
          return;
        }

        if (!code) {
          setStatus('error');
          setMessage('No authorization code received');
          
          // Send error to parent window if popup
          if (window.opener) {
            window.opener.postMessage({
              type: 'GOOGLE_OAUTH_ERROR',
              message: 'No authorization code received'
            }, window.location.origin);
          }
          return;
        }

        // Send code to backend
        const response = await fetch('http://localhost:8000/google/oauth/callback', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            authorization_code: code,
            state: state
          })
        });

        const data = await response.json();

        if (response.ok) {
          setStatus('success');
          setMessage('Google Calendar authorization successful!');
          
          // Send success message to parent window (if opened as popup)
          if (window.opener) {
            window.opener.postMessage({
              type: 'GOOGLE_OAUTH_SUCCESS'
            }, window.location.origin);
            
            // Close popup after a short delay
            setTimeout(() => {
              window.close();
            }, 2000);
          } else {
            // Redirect to channel linking page after 2 seconds if not a popup
            setTimeout(() => {
              navigate('/channel-linking');
            }, 2000);
          }
        } else {
          setStatus('error');
          setMessage(data.detail || 'Authorization failed');
          
          // Send error message to parent window (if opened as popup)
          if (window.opener) {
            window.opener.postMessage({
              type: 'GOOGLE_OAUTH_ERROR',
              message: data.detail || 'Authorization failed'
            }, window.location.origin);
          }
        }

      } catch (error) {
        setStatus('error');
        setMessage('Error processing authorization');
        console.error('OAuth callback error:', error);
        
        // Send error to parent window if popup
        if (window.opener) {
          window.opener.postMessage({
            type: 'GOOGLE_OAUTH_ERROR',
            message: 'Error processing authorization'
          }, window.location.origin);
        }
      }
    };

    handleCallback();
  }, [location, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-6">
        <div className="text-center">
          {status === 'processing' && (
            <>
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <h2 className="text-xl font-semibold text-gray-800 mb-2">Processing Authorization</h2>
            </>
          )}
          
          {status === 'success' && (
            <>
              <div className="text-green-500 text-5xl mb-4">✅</div>
              <h2 className="text-xl font-semibold text-green-800 mb-2">Success!</h2>
            </>
          )}
          
          {status === 'error' && (
            <>
              <div className="text-red-500 text-5xl mb-4">❌</div>
              <h2 className="text-xl font-semibold text-red-800 mb-2">Error</h2>
            </>
          )}
          
          <p className="text-gray-600">{message}</p>
          
          {status === 'success' && window.opener && (
            <p className="text-sm text-gray-500 mt-2">This window will close automatically...</p>
          )}
          
          {status === 'success' && !window.opener && (
            <p className="text-sm text-gray-500 mt-2">Redirecting to configuration...</p>
          )}
          
          {status === 'error' && !window.opener && (
            <button
              onClick={() => navigate('/channel-linking')}
              className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
            >
              Back to Configuration
            </button>
          )}
          
          {status === 'error' && window.opener && (
            <button
              onClick={() => window.close()}
              className="mt-4 px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors"
            >
              Close
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default GoogleOAuthCallback;
