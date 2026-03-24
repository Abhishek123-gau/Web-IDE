import React from "react";

const DisplayArea = ({text, className}) => {
  return (
    <div className={className}>
      {text}
    </div>
  );
};

export default DisplayArea;