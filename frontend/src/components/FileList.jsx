import React, { useState, useEffect } from 'react';
import { getFiles, deleteFile } from '../api/api';
import { FileText, Trash2, Loader2, CheckCircle, AlertCircle } from 'lucide-react';

const FileList = ({ storeId, refreshTrigger }) => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (storeId) {
      fetchFiles();
    } else {
      setFiles([]);
    }
  }, [storeId, refreshTrigger]);

  const fetchFiles = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getFiles(storeId);
      setFiles(data.files);
    } catch (err) {
      console.error(err);
      setError('Failed to load files');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (fileId) => {
    if (!window.confirm('Delete this file?')) return;
    
    try {
      await deleteFile(storeId, fileId);
      setFiles(files.filter(f => f.id !== fileId));
    } catch (err) {
      console.error(err);
      alert('Failed to delete file');
    }
  };

  if (!storeId) return null;

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="px-4 py-3 border-b bg-gray-50 flex justify-between items-center">
        <h3 className="font-semibold text-gray-700 flex items-center gap-2">
          <FileText className="w-4 h-4" /> 
          Files in Store
        </h3>
        <span className="text-xs text-gray-500">{files.length} files</span>
      </div>

      {loading ? (
        <div className="p-8 text-center text-gray-500">
          <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />
          Loading files...
        </div>
      ) : error ? (
        <div className="p-4 text-red-600 text-sm bg-red-50">{error}</div>
      ) : files.length === 0 ? (
        <div className="p-8 text-center text-gray-400 text-sm">
          No files uploaded yet.
        </div>
      ) : (
        <div className="divide-y divide-gray-100 max-h-96 overflow-y-auto">
          {files.map((file) => (
            <div key={file.id} className="p-3 hover:bg-gray-50 flex justify-between items-center group">
              <div className="flex items-center gap-3 overflow-hidden">
                <div className="bg-blue-100 p-2 rounded text-blue-600">
                  <FileText className="w-4 h-4" />
                </div>
                <div className="min-w-0">
                  <div className="text-sm font-medium text-gray-900 truncate" title={file.display_name}>
                    {file.display_name}
                  </div>
                  <div className="text-xs text-gray-500 flex items-center gap-2">
                    <span>{new Date(file.upload_date).toLocaleDateString()}</span>
                    <span className={`flex items-center gap-1 ${
                      file.status === 'COMPLETED' ? 'text-green-600' : 'text-amber-600'
                    }`}>
                      {file.status === 'COMPLETED' ? (
                        <CheckCircle className="w-3 h-3" />
                      ) : (
                        <Loader2 className="w-3 h-3 animate-spin" />
                      )}
                      {file.status}
                    </span>
                  </div>
                </div>
              </div>
              
              <button
                onClick={() => handleDelete(file.id)}
                className="text-gray-400 hover:text-red-600 p-2 opacity-0 group-hover:opacity-100 transition-opacity"
                title="Delete File"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FileList;
