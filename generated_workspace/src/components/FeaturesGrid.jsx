import React from 'react';
// Assuming FeatureItem is a separate component
import FeatureItem from './FeatureItem';

const FeaturesGrid = ({ className }) => {
    return (
        <div className={`${className} bg-white rounded-2xl shadow-xl`}>
            <FeatureItem 
                title="Title 1" 
                description="Description for feature 1." 
                iconClassName="fas fa-user" // assuming you're using font awesome icons
            />
            <FeatureItem 
                title="Title 2" 
                description="Description for feature 2." 
                iconClassName="fas fa-heart"
            />
            <FeatureItem 
                title="Title 3" 
                description="Description for feature 3." 
                iconClassName="fas fa-bell"
            />
        </div>
    );
};

export default FeaturesGrid;