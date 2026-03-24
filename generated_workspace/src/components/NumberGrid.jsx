import React from 'react';
// Assuming you have a Button component at './Button'
import Button from './Button';

const NumberGrid = ({ className, onNumberClick }) => {
    return (
        <div className={`${className || ''} bg-white rounded-2xl shadow-inner grid grid-cols-3 gap-3 p-2`}>
            {[7, 8, 9, 4, 5, 6, 1, 2, 3, 0, '.', '='].map((item) => (
                <Button 
                    key={item} 
                    label={item.toString()} 
                    onClick={() => onNumberClick(item.toString())} 
                    variant={item === '=' ? 'primary' : 'secondary'}
                />
            ))}
        </div>
    );
};

export default NumberGrid;