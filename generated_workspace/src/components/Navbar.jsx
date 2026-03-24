import React from 'react';

const Navbar = ({ className }) => {
    return (
        <nav className={`${className} w-full px-6 py-4 flex items-center justify-between`}>
            <div>
                <a href="/" className="text-white text-2xl font-bold">Logo</a>
            </div>
            <div className="flex space-x-8">
                {/* Child components can be added here */}
            </div>
        </nav>
    );
};

export default Navbar;