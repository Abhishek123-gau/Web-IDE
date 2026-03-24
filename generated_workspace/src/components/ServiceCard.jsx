import React from 'react';

const ServiceCard = ({ icon, title, description }) => {
    return (
        <div className="p-6 bg-white rounded-2xl shadow-xl hover:scale-105 transition-all">
            <i className={`fas fa-cog text-4xl mb-4`}></i>
            <h3 className="text-2xl font-bold mb-2">{title}</h3>
            <p className="text-gray-600">{description}</p>
        </div>
    );
};

export default ServiceCard;