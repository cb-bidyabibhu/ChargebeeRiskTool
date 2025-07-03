import React, { useState } from 'react';

const isObject = (val) => val && typeof val === 'object' && !Array.isArray(val);
const isArray = Array.isArray;

const ExpandableDataView = ({ data, label }) => {
  const [expanded, setExpanded] = useState(false);

  if (data === null || data === undefined) return null;

  // Render primitive values
  if (typeof data !== 'object') {
    if (label && (label === 'source' || label === 'source_url') && typeof data === 'string' && data.startsWith('http')) {
      return (
        <div className="flex items-center space-x-2">
          <span className="font-medium text-gray-700">{label}:</span>
          <a href={data} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline break-all">{data}</a>
        </div>
      );
    }
    return (
      <div className="flex items-center space-x-2">
        {label && <span className="font-medium text-gray-700">{label}:</span>}
        <span className="text-gray-900">{String(data)}</span>
      </div>
    );
  }

  // Render arrays
  if (isArray(data)) {
    return (
      <div className="ml-4">
        {label && (
          <button
            className="text-left w-full flex items-center space-x-2 py-1"
            onClick={() => setExpanded((e) => !e)}
          >
            <span className="font-medium text-gray-700">{label} [{data.length}]</span>
            <span className="text-xs text-gray-500">[{expanded ? '-' : '+'}]</span>
          </button>
        )}
        {expanded && (
          <div className="pl-4 border-l border-gray-200">
            {data.map((item, idx) => (
              <ExpandableDataView key={idx} data={item} label={null} />
            ))}
          </div>
        )}
      </div>
    );
  }

  // Render objects
  return (
    <div className="ml-2">
      {label && (
        <button
          className="text-left w-full flex items-center space-x-2 py-1"
          onClick={() => setExpanded((e) => !e)}
        >
          <span className="font-medium text-gray-700">{label}</span>
          <span className="text-xs text-gray-500">[{expanded ? '-' : '+'}]</span>
        </button>
      )}
      {expanded && (
        <div className="pl-4 border-l border-gray-200">
          {Object.entries(data).map(([key, value]) => (
            <ExpandableDataView key={key} data={value} label={key} />
          ))}
        </div>
      )}
    </div>
  );
};

export default ExpandableDataView; 