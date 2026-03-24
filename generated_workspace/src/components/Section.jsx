import React from "react";
import ServiceCard from './ServiceCard'; // Assuming you have a ServiceCard component

const Section = ({ title, description }) => {
  return (
    <section className="max-w-md mx-auto pt-12 pb-6 text-center sm:pt-16 sm:pb-10 md:px-4 lg:px-8 xl:px-10 2xl:px-12">
      <div className="relative">
        <h2 className="text-3xl font-extrabold tracking-tight text-gray-900 sm:text-4xl">{title}</h2>
        <p className="mt-4 text-lg leading-6 text-gray-500">{description}</p>
      </div>
      
      {/* Render ServiceCards */}
      <ServiceCard />
      <ServiceCard />
    </section>
  );
};

export default Section;