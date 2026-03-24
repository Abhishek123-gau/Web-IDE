
import React from "react";

const Header = ({ title }) => {
  return (
    <header className="flex justify-center items-center h-20 bg-blue-500 text-white font-bold shadow-lg">
      <h1 className="text-3xl md:text-4xl lg:text-5xl">{title}</h1>
    </header>
  );
};

export default Header;