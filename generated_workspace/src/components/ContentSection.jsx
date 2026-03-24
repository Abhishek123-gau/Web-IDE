import React from 'react';
import InputField from './InputField';
import DropdownMenu from './DropdownMenu';
import Button from './Button';
import OutputField from './OutputField';

const ContentSection = ({ className }) => {
    return (
        <div className={`${className} bg-white rounded-2xl shadow-xl p-4 space-y-4`}>
            <InputField />
            <DropdownMenu />
            <Button />
            <OutputField />
        </div>
    );
};

export default ContentSection;