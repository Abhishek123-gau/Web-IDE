import React from 'react';

const DropdownMenu = ({ options = [], defaultValue, className }) => {
  return (
    <div className={`${className || ''}`}>
      <select className="w-full px-4 py-2 rounded-lg shadow-md hover:shadow-lg focus:outline-none focus:ring-2 transition-all" defaultValue={defaultValue}>
        {options && options.map((option, index) => (
          <option key={index} value={option} className="capitalize">
            {option}
          </option>
        ))}
      </select>
    </div>
  );
};

export default DropdownMenu;