import React from 'react';

const FeatureItem = ({ icon, title, description }) => {
    return (
        <div className="p-6 bg-white rounded-2xl shadow-xl flex items-start">
            <i className={`${icon} text-5xl mr-4 text-blue-500`}></i>
            <div>
                <h3 className="text-lg font-bold mb-2">{title}</h3>
                <p className="text-gray-600">{description}</p>
            </div>
        </div>
    );
};

export default FeatureItem;