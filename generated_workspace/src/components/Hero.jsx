import React from 'react';

const Hero = ({ title, subtitle, buttonText }) => {
  return (
    <div className="bg-gradient-to-r from-cyan-500 to-blue-500 p-8 rounded-2xl shadow-xl text-white max-w-md mx-auto">
      <h1 className="text-4xl font-bold mb-6">{title}</h1>
      <p className="mb-8">{subtitle}</p>
      <button className="bg-white text-gray-800 rounded-full px-8 py-2 hover:scale-105 transition-all">
        {buttonText}
      </button>
    </div>
  );
};

export default Hero;