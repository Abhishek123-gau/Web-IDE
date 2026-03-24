import React from 'react';
import Navbar from '../components/Navbar';
import HeroSection from '../components/HeroSection';
import FeaturesGrid from '../components/FeaturesGrid';

const Home = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <Navbar className="bg-black sticky top-0 z-10"/>
      <HeroSection className="flex items-center justify-center h-screen bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 text-white"/>
      <FeaturesGrid className="grid grid-cols-1 md:grid-cols-3 gap-4 p-6"/>
    </div>
  );
};

export default Home;