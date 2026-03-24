import React from 'react';

const BuySellOptionsList = ({ className }) => {
    return (
        <div 
            className={`${className} flex flex-col rounded-2xl shadow-xl p-6 space-y-4 hover:scale-105 transition-all`}>
            <h3 className="text-lg font-bold">Buy/Sell Options</h3>
            {/* You can add more options here as needed */}
        </div>
    );
};

export default BuySellOptionsList;