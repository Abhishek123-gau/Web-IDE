
import React from 'react';
import Button from './Button'; // Assuming Button is imported from its own file

const NumberButtonsGrid = () => {
    const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9];

    return (
        <div className="grid grid-cols-3 gap-4 p-4 max-w-md mx-auto bg-white rounded-xl shadow-md flex items-center">
            {numbers.map((number) => (
                <Button key={number} className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                    {number}
                </Button>
            ))}
        </div>
    );
};

export default NumberButtonsGrid;
