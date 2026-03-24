import React from 'react';

const ProfilePicture = ({ src, className }) => {
  return (
    <img src={src} className={className} />
  );
};

export default ProfilePicture;