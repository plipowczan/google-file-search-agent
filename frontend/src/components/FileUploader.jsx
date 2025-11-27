import React, { useState, useRef } from 'react';
import { uploadFile } from '../api/api';
import { Upload, Loader2, FileText } from 'lucide-react';

const FileUploader = ({ storeId, onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!storeId) {
      setError('Please select a store first.');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      await uploadFile(storeId, file);
      onUploadSuccess();
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      console.error(err);
      setError('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="mb-6">
      <div 
        className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          storeId ? 'border-gray-300 hover:border-blue-500 cursor-pointer bg-gray-50' : 'border-gray-200 bg-gray-100 cursor-not-allowed'
        }`}
        onClick={() => storeId && fileInputRef.current?.click()}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
          disabled={!storeId || uploading}
        />
        
        {uploading ? (
          <div className="flex flex-col items-center text-blue-600">
            <Loader2 className="w-8 h-8 animate-spin mb-2" />
            <span className="text-sm font-medium">Uploading & Indexing...</span>
            <span className="text-xs text-gray-500 mt-1">This may take a moment</span>
          </div>
        ) : (
          <div className="flex flex-col items-center text-gray-500">
            <Upload className="w-8 h-8 mb-2" />
            <span className="text-sm font-medium">
              {storeId ? 'Click to upload a file' : 'Select a store to upload files'}
            </span>
            <span className="text-xs mt-1">PDF, DOCX, TXT, CSV supported</span>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-2 text-sm text-red-600 bg-red-50 p-2 rounded">
          {error}
        </div>
      )}
    </div>
  );
};

export default FileUploader;
