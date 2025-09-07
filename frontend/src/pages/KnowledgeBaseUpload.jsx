import React, { useState, useEffect } from "react";
import DownloadIcon from "../assets/download.png";
import DeleteIcon from "../assets/delete.png";
import Toast from "../components/Toast";
import useSuccessNotification from "../hooks/useSuccessNotification";

const KnowledgeBaseUpload = () => {
  const [files, setFiles] = useState([]); // File objects
  const [descriptions, setDescriptions] = useState({}); // index -> description
  const [message, setMessage] = useState("");
  const [uploading, setUploading] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [studyStatus, setStudyStatus] = useState("idle");
  const [studyProcessed, setStudyProcessed] = useState([]);
  const [studyError, setStudyError] = useState(null);
  const [polling, setPolling] = useState(null);
  const [deletingIds, setDeletingIds] = useState([]);
  
  // Toast notification state and hook
  const [toast, setToast] = useState({ show: false, type: '', title: '', message: '' });
  const { showSuccess, showError } = useSuccessNotification(setToast);

  const loadDocuments = async () => {
    try {
      const resp = await fetch(
        "http://localhost:8000/knowledge_base/documents"
      );
      if (resp.ok) {
        const data = await resp.json();
        setDocuments(data);
      }
    } catch (e) {
      /* ignore */
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const pollStudy = () => {
    const id = setInterval(async () => {
      try {
        const r = await fetch(
          "http://localhost:8000/knowledge_base/vectorise/status"
        );
        if (r.ok) {
          const data = await r.json();
          setStudyStatus(data.status);
          setStudyProcessed(data.processed || []);
          setStudyError(data.error || null);
          if (data.status === "completed" || data.status === "error") {
            clearInterval(id);
            setPolling(null);
            loadDocuments();
            
            // Show success notification when study completes
            if (data.status === "completed") {
              showSuccess('Bot Study Complete', 'The bot has successfully learned from your documents.');
            } else if (data.status === "error") {
              showError('Bot Study Failed', data.error || 'An error occurred during the study process.');
            }
          }
        }
      } catch (e) {
        /* ignore */
      }
    }, 1500);
    setPolling(id);
  };

  const startStudy = async () => {
    try {
      const resp = await fetch(
        "http://localhost:8000/knowledge_base/vectorise",
        { method: "POST" }
      );
      if (resp.ok) {
        const data = await resp.json();
        setStudyStatus(data.status);
        setStudyProcessed([]);
        setStudyError(null);
        if (!polling) pollStudy();
      }
    } catch (e) {
      /* ignore */
    }
  };

  const handleDownload = async (id, fileName) => {
    try {
      const resp = await fetch(
        `http://localhost:8000/knowledge_base/documents/${id}/download`
      );
      if (!resp.ok) return;
      const blob = await resp.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = fileName || "document";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      /* ignore */
    }
  };

  const handleDelete = async (id) => {
    setDeletingIds((prev) => [...prev, id]);
    try {
      const resp = await fetch(
        `http://localhost:8000/knowledge_base/documents/${id}`,
        { method: "DELETE" }
      );
      if (resp.ok) {
        await loadDocuments();
        showSuccess('File Deleted', 'The document has been successfully removed from the knowledge base.');
      } else {
        showError('Delete Failed', 'Failed to delete the document. Please try again.');
      }
    } catch (e) {
      showError('Delete Error', 'An error occurred while deleting the document.');
    } finally {
      setDeletingIds((prev) => prev.filter((x) => x !== id));
    }
  };

  const handleFilesChange = (e) => {
    setFiles(Array.from(e.target.files));
    setDescriptions({});
    setMessage("");
  };

  const handleDescriptionChange = (idx, value) => {
    setDescriptions((prev) => ({ ...prev, [idx]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    if (!files.length) {
      setMessage("Please select at least one file.");
      return;
    }
    setUploading(true);
    const formData = new FormData();
    files.forEach((f) => formData.append("files", f));
    // Align descriptions array to files ordering
    const descArray = files.map((_, idx) => descriptions[idx] || "");
    descArray.forEach((d) => formData.append("descriptions", d));
    try {
      const resp = await fetch("http://localhost:8000/knowledge_base/upload", {
        method: "POST",
        body: formData,
      });
      const data = await resp.json();
      if (resp.ok) {
        setMessage(data.message || "Documents uploaded successfully!");
        setFiles([]);
        setDescriptions({});
        e.target.reset();
        loadDocuments();
        showSuccess('Files Uploaded', `${files.length} document(s) have been successfully uploaded to the knowledge base.`);
      } else {
        const errorMessage = typeof data.detail === "string"
          ? data.detail
          : JSON.stringify(data.detail) || "Failed to upload documents.";
        setMessage(errorMessage);
        showError('Upload Failed', errorMessage);
      }
    } catch (err) {
      const errorMessage = "An error occurred during documents upload.";
      setMessage(errorMessage);
      showError('Upload Error', errorMessage);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="spacing-responsive">
      <h1 className="text-responsive-xl mb-4">Knowledge Base</h1>
      <div className="rounded-lg p-2 md:p-4 lg:p-6 border border-black">
        <h2 className="text-responsive-lg mt-2">Current Documents</h2>
        <div className="mt-2 border rounded p-2 max-h-64 md:max-h-80 overflow-auto bg-gray-50 text-responsive-xs">
          {documents.length === 0 && (
            <p className="italic">No documents uploaded.</p>
          )}
          {documents.length > 0 && (
            <div className="table-responsive">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b">
                    <th className="py-1 pr-2">File</th>
                    <th className="py-1 pr-2 hidden sm:table-cell">Type</th>
                    <th className="py-1 pr-2 hidden md:table-cell">Size</th>
                    <th className="py-1 pr-2 hidden lg:table-cell">Description</th>
                    <th className="py-1 pr-2 hidden sm:table-cell">Uploaded</th>
                    <th className="py-1 pr-2">Status</th>
                    <th className="py-1 pr-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((doc) => (
                    <tr key={doc.id} className="border-b last:border-none">
                      <td className="py-1 pr-2 break-all max-w-0 truncate">{doc.file_name}</td>
                      <td className="py-1 pr-2 hidden sm:table-cell">{doc.content_type || "-"}</td>
                      <td className="py-1 pr-2 hidden md:table-cell">
                        {doc.size_bytes != null ? doc.size_bytes : "-"}
                      </td>
                      <td className="py-1 pr-2 hidden lg:table-cell">{doc.description || "-"}</td>
                      <td className="py-1 pr-2 hidden sm:table-cell">
                        {doc.created_at
                          ? new Date(doc.created_at).toLocaleDateString()
                          : "-"}
                      </td>
                      <td className="py-1 pr-2">{doc.study_status || "-"}</td>
                      <td className="py-1 pr-2 space-x-1 flex">
                        <button
                          onClick={() => handleDownload(doc.id, doc.file_name)}
                          className="px-1 py-0.5 border border-black rounded text-white text-[10px] bg-blue-500 hover:bg-blue-600"
                        >
                          <img src={DownloadIcon} alt="Download" className="w-3 h-3"/>
                        </button>
                        <button
                          disabled={deletingIds.includes(doc.id)}
                          onClick={() => handleDelete(doc.id)}
                          className="px-1 py-0.5 border border-black rounded text-white text-[10px] disabled:opacity-50 bg-red-500 hover:bg-red-600"
                        >
                          {deletingIds.includes(doc.id) ? "..." : <img src={DeleteIcon} alt="Delete" className="w-3 h-3"/>}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
        
        <h2 className="text-responsive-lg mt-6">Add Documents</h2>
        <div className="mt-4 flex flex-col sm:flex-row items-start sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
          <button
            type="button"
            onClick={startStudy}
            disabled={studyStatus === "running"}
            className="border border-black rounded-md px-4 py-2 bg-purple-600 text-white hover:bg-purple-700 disabled:opacity-50 text-responsive-sm"
          >
            {studyStatus === "running" ? "Studying..." : "Bot Study"}
          </button>
          <div className="text-responsive-xs">
            Status: {studyStatus}
            {studyError && (
              <span className="text-red-600 ml-2">Error: {studyError}</span>
            )}
            {studyProcessed.length > 0 && studyStatus === "completed" && (
              <span className="ml-2 block sm:inline">
                Processed: {studyProcessed.join(", ")}
              </span>
            )}
          </div>
        </div>
        
        <form onSubmit={handleSubmit} className="flex flex-col mt-4 space-y-4">
          <div>
            <label className="block text-responsive-sm font-medium text-gray-700">
              Select Files (PDF/Text)
            </label>
            <input
              type="file"
              accept=".pdf,.txt"
              multiple
              className="mt-1 block w-full text-responsive-xs text-gray-500 
                file:mr-2 file:py-2 file:px-3 file:rounded-md file:border-0 
                file:text-responsive-xs file:font-semibold file:bg-blue-50 
                file:text-blue-700 hover:file:bg-blue-100"
              onChange={handleFilesChange}
              required
            />
          </div>
          
          {files.length > 0 && (
            <div className="space-y-3">
              {files.map((f, idx) => (
                <div key={idx} className="border rounded p-3 bg-white">
                  <div className="text-responsive-xs font-semibold break-all mb-2">
                    {f.name}
                  </div>
                  <input
                    type="text"
                    placeholder="Description (optional)"
                    className="block w-full rounded-md border-gray-300 shadow-sm text-responsive-xs 
                      focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                    value={descriptions[idx] || ""}
                    onChange={(e) =>
                      handleDescriptionChange(idx, e.target.value)
                    }
                  />
                </div>
              ))}
            </div>
          )}
          
          <button
            type="submit"
            className="flex justify-center border border-black rounded-md px-6 py-2 
              cursor-pointer bg-green-500 text-white hover:bg-green-600 
              disabled:opacity-50 text-responsive-sm font-medium"
            disabled={uploading}
          >
            {uploading ? "Uploading..." : "Upload Documents"}
          </button>
        </form>
        
        {message && (
          <p className="mt-3 text-responsive-sm p-3 rounded-md bg-gray-50 border border-gray-200">
            {message}
          </p>
        )}
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

export default KnowledgeBaseUpload;
