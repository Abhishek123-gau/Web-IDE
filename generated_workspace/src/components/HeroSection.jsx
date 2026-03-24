import React from "react";
import Text from './Text'; // Assuming you have a Text component

const HeroSection = ({ className }) => {
    return (
        <section className={`${className}`}>
            <Text />
        </section>
    );
};

export default HeroSection;