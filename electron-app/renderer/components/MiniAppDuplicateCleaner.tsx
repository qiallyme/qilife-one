import React, { useState } from 'react';

export const MiniAppDuplicateCleaner: React.FC = () => {
  const [roots, setRoots] = useState('');
  const [output, setOutput] = useState<string | null>(null);

  const runCleaner = async () => {
    const rootArray = roots
      .split(',')
      .map((s) => s.trim())
      .filter((s) => s !== '');
    const result = await (window as any).electronAPI.runDuplicateCleaner({
      roots: rootArray,
      maxDepth: -1,
      weights: { name: 0.6, size: 0.4 },
      reviewThreshold: 0.9,
      preferThreshold: 0.971,
      aiThreshold: 0.98,
      action: 'report',
      output: undefined,
    });
    setOutput(result);
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-semibold mb-2">Duplicate Cleaner</h2>
      <label className="block mb-2">
        Roots (comma separated):
        <input
          type="text"
          className="mt-1 block w-full border rounded"
          value={roots}
          onChange={(e) => setRoots(e.target.value)}
        />
      </label>
      <button
        className="bg-blue-500 text-white px-4 py-2 rounded"
        onClick={runCleaner}
      >
        Scan
      </button>
      {output && (
        <pre className="mt-4 p-2 bg-gray-100 rounded overflow-auto h-48">
          {output}
        </pre>
      )}
    </div>
  );
};
