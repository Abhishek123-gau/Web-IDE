import React from 'react';

const Footer = ({ links }) => {
  return (
    <footer className="bg-gray-800 text-white p-6 flex justify-center items-center space-x-4 hover:scale-105 transition-all rounded-2xl shadow-xl">
      {links.map((link, index) => (
        <a key={index} href="#" className="hover:text-gray-300">
          {link}
        </a>
      ))}
    </footer>
  );
};

export default Footer;