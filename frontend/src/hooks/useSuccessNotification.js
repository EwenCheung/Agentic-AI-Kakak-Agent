import { useState, useCallback } from 'react';

const useSuccessNotification = () => {
  const [notification, setNotification] = useState({
    show: false,
    message: '',
    type: 'success'
  });

  const showSuccess = useCallback((message) => {
    setNotification({
      show: true,
      message,
      type: 'success'
    });
  }, []);

  const showError = useCallback((message) => {
    setNotification({
      show: true,
      message,
      type: 'error'
    });
  }, []);

  const showWarning = useCallback((message) => {
    setNotification({
      show: true,
      message,
      type: 'warning'
    });
  }, []);

  const showInfo = useCallback((message) => {
    setNotification({
      show: true,
      message,
      type: 'info'
    });
  }, []);

  const hideNotification = useCallback(() => {
    setNotification(prev => ({
      ...prev,
      show: false
    }));
  }, []);

  return {
    notification,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    hideNotification
  };
};

export default useSuccessNotification;