import { useCallback } from 'react';

const useSuccessNotification = (setToast) => {
  const showSuccess = useCallback((title, message) => {
    setToast({
      show: true,
      type: 'success',
      title,
      message
    });
  }, [setToast]);

  const showError = useCallback((title, message) => {
    setToast({
      show: true,
      type: 'error',
      title,
      message
    });
  }, [setToast]);

  const showWarning = useCallback((title, message) => {
    setToast({
      show: true,
      type: 'warning',
      title,
      message
    });
  }, [setToast]);

  const showInfo = useCallback((title, message) => {
    setToast({
      show: true,
      type: 'info',
      title,
      message
    });
  }, [setToast]);

  return {
    showSuccess,
    showError,
    showWarning,
    showInfo
  };
};

export default useSuccessNotification;