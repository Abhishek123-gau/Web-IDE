import React from 'react';

const InputField = ({ placeholder, className }) => {
    return (
        <input type='text' 
            className={className} 
            placeholder={placeholder} />
    );
};

export default InputField;