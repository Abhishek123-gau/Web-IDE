import React from "react";
import NumberButton from './NumberButton';
import OperationButton from './OperationButton';

const ButtonContainer = () => {
    return (
        <div className="flex flex-wrap justify-center items-center h-screen bg-gray-100">
            <NumberButton value={7} />
            <NumberButton value={8} />
            <NumberButton value={9} />
            <OperationButton symbol={'+'} />
            <NumberButton value={4} />
            <NumberButton value={5} />
            <NumberButton value={6} />
            <OperationButton symbol={'-'} />
            <NumberButton value={1} />
            <NumberButton value={2} />
            <NumberButton value={3} />
            <OperationButton symbol={'*'} />
            <NumberButton value={0} />
            <OperationButton symbol={'/'} />
        </div>
    );
};

export default ButtonContainer;