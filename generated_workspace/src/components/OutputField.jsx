import React from 'react';

const OutputField = ({ content, className }) => {
    return (
        <div className={`rounded-lg shadow-md ${className}`}>
            <p className="text-left p-2">{content}</p>
        </div>
    );
};

export default OutputField;